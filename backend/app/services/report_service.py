from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.report import Report
from app.models.user import User
from app.schemas.report import ReportCreate, ReportOut


def _label_resolver(db: Session, reports: list[Report]):
    item_ids = {r.target_id for r in reports if r.target_type == 1}
    user_ids = {r.target_id for r in reports if r.target_type == 2}

    items: dict[int, str] = {}
    if item_ids:
        items = {
            item.id: item.title
            for item in db.scalars(select(Item).where(Item.id.in_(item_ids)))
        }
    users: dict[int, str] = {}
    if user_ids:
        users = {
            user.id: user.student_id
            for user in db.scalars(select(User).where(User.id.in_(user_ids)))
        }

    def resolve(report: Report) -> str:
        if report.target_type == 1:
            return f"商品：{items.get(report.target_id, report.target_id)}"
        return f"用户：{users.get(report.target_id, report.target_id)}"

    return resolve


def _to_out(
    report: Report,
    reporter_student_id: str | None,
    target_label: str,
) -> ReportOut:
    return ReportOut(
        id=report.id,
        reporter_id=report.reporter_id,
        target_type=report.target_type,
        target_id=report.target_id,
        reason=report.reason,
        status=report.status,
        handler_id=report.handler_id,
        handle_note=report.handle_note,
        created_at=report.created_at,
        handled_at=report.handled_at,
        reporter_student_id=reporter_student_id,
        target_label=target_label,
    )


def create_report(
    db: Session, user: User, payload: ReportCreate
) -> Report:
    if payload.target_type == 1:
        target = db.get(Item, payload.target_id)
        if target is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="被举报商品不存在"
            )
        if target.user_id == user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能举报自己发布的商品",
            )
    else:
        target_user = db.get(User, payload.target_id)
        if target_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="被举报用户不存在"
            )
        if target_user.id == user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="不能举报自己"
            )

    pending = db.scalar(
        select(Report.id).where(
            Report.reporter_id == user.id,
            Report.target_type == payload.target_type,
            Report.target_id == payload.target_id,
            Report.status == 0,
        )
    )
    if pending is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该对象已有待处理的举报",
        )

    report = Report(
        reporter_id=user.id,
        target_type=payload.target_type,
        target_id=payload.target_id,
        reason=payload.reason.strip(),
        status=0,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def list_my_reports(
    db: Session, user: User, page: int, size: int
) -> tuple[int, list[ReportOut]]:
    total = db.scalar(
        select(func.count())
        .select_from(Report)
        .where(Report.reporter_id == user.id)
    ) or 0
    reports = db.scalars(
        select(Report)
        .where(Report.reporter_id == user.id)
        .order_by(Report.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()
    resolve = _label_resolver(db, list(reports))
    return total, [
        _to_out(report, user.student_id, resolve(report)) for report in reports
    ]


def list_reports(
    db: Session,
    page: int,
    size: int,
    report_status: int | None = None,
) -> tuple[int, list[ReportOut]]:
    condition = Report.status == report_status if report_status is not None else None
    count_stmt = select(func.count()).select_from(Report)
    rows_stmt = select(Report, User.student_id).join(
        User, Report.reporter_id == User.id
    )
    if condition is not None:
        count_stmt = count_stmt.where(condition)
        rows_stmt = rows_stmt.where(condition)

    total = db.scalar(count_stmt) or 0
    rows = db.execute(
        rows_stmt.order_by(Report.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()
    reports = [report for report, _ in rows]
    resolve = _label_resolver(db, reports)
    return total, [
        _to_out(report, reporter_student_id, resolve(report))
        for report, reporter_student_id in rows
    ]


def handle_report(
    db: Session,
    admin: User,
    report_id: int,
    new_status: int,
    note: str | None,
) -> Report:
    report = db.get(Report, report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="举报工单不存在"
        )
    if report.status != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="该举报已处理"
        )

    report.status = new_status
    report.handler_id = admin.id
    report.handle_note = (note or "").strip() or None
    report.handled_at = datetime.now()
    db.commit()
    db.refresh(report)
    return report
