from datetime import datetime, timedelta
from math import ceil

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from app.models.admin_application import AdminApplication
from app.models.user import User
from app.schemas.admin_application import AdminApplicationOut

COOLDOWN = timedelta(days=3)


def _to_out(
    application: AdminApplication,
    applicant_student_id: str | None = None,
    reviewer_student_id: str | None = None,
) -> AdminApplicationOut:
    return AdminApplicationOut(
        id=application.id,
        user_id=application.user_id,
        reason=application.reason,
        status=application.status,
        reviewer_id=application.reviewer_id,
        review_note=application.review_note,
        created_at=application.created_at,
        reviewed_at=application.reviewed_at,
        applicant_student_id=applicant_student_id,
        reviewer_student_id=reviewer_student_id,
    )


def apply(db: Session, user: User, reason: str) -> AdminApplication:
    if user.role != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="当前角色无需申请"
        )

    pending = db.scalar(
        select(AdminApplication.id).where(
            AdminApplication.user_id == user.id,
            AdminApplication.status == 0,
        )
    )
    if pending is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已有待审批的管理员申请",
        )

    last_rejected = db.scalar(
        select(AdminApplication)
        .where(
            AdminApplication.user_id == user.id,
            AdminApplication.status == 2,
        )
        .order_by(AdminApplication.created_at.desc())
        .limit(1)
    )
    if last_rejected is not None:
        reference = last_rejected.reviewed_at or last_rejected.created_at
        remaining = COOLDOWN - (datetime.now() - reference)
        if remaining > timedelta(0):
            days = ceil(remaining.total_seconds() / 86400)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"距上次驳回未满 3 天，请 {days} 天后再申请",
            )

    application = AdminApplication(
        user_id=user.id, reason=reason.strip(), status=0
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def list_my(
    db: Session, user: User, page: int, size: int
) -> tuple[int, list[AdminApplicationOut]]:
    total = db.scalar(
        select(func.count())
        .select_from(AdminApplication)
        .where(AdminApplication.user_id == user.id)
    ) or 0
    applications = db.scalars(
        select(AdminApplication)
        .where(AdminApplication.user_id == user.id)
        .order_by(AdminApplication.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()

    reviewer_ids = {
        application.reviewer_id
        for application in applications
        if application.reviewer_id is not None
    }
    reviewers: dict[int, str] = {}
    if reviewer_ids:
        reviewers = {
            reviewer.id: reviewer.student_id
            for reviewer in db.scalars(
                select(User).where(User.id.in_(reviewer_ids))
            )
        }

    return total, [
        _to_out(
            application,
            applicant_student_id=user.student_id,
            reviewer_student_id=reviewers.get(application.reviewer_id),
        )
        for application in applications
    ]


def list_for_admin(
    db: Session,
    page: int,
    size: int,
    application_status: int | None = None,
) -> tuple[int, list[AdminApplicationOut]]:
    condition = (
        AdminApplication.status == application_status
        if application_status is not None
        else None
    )
    count_stmt = select(func.count()).select_from(AdminApplication)
    if condition is not None:
        count_stmt = count_stmt.where(condition)
    total = db.scalar(count_stmt) or 0

    applicant = aliased(User)
    reviewer = aliased(User)
    stmt = (
        select(AdminApplication, applicant.student_id, reviewer.student_id)
        .join(applicant, AdminApplication.user_id == applicant.id)
        .outerjoin(reviewer, AdminApplication.reviewer_id == reviewer.id)
    )
    if condition is not None:
        stmt = stmt.where(condition)
    rows = db.execute(
        stmt.order_by(AdminApplication.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()

    return total, [
        _to_out(
            application,
            applicant_student_id=applicant_student_id,
            reviewer_student_id=reviewer_student_id,
        )
        for application, applicant_student_id, reviewer_student_id in rows
    ]


def review(
    db: Session,
    admin: User,
    application_id: int,
    new_status: int,
    note: str | None,
) -> AdminApplication:
    application = db.get(AdminApplication, application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="申请记录不存在"
        )
    if application.status != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="该申请已处理"
        )

    applicant = db.get(User, application.user_id)
    if applicant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="申请人不存在"
        )
    if applicant.status != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="该用户已被封禁"
        )

    if new_status == 1:
        if applicant.role != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户已是管理员",
            )
        applicant.role = 1

    application.status = new_status
    application.reviewer_id = admin.id
    application.review_note = (note or "").strip() or None
    application.reviewed_at = datetime.now()
    db.commit()
    db.refresh(application)
    return application
