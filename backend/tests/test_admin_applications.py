from datetime import datetime, timedelta

from sqlalchemy import select

from app.models.admin_application import AdminApplication
from app.models.user import User


def test_apply_and_duplicate(client, student, admin):
    payload = {"reason": "希望协助审核商品并处理举报，每周可在线十小时"}

    created = client.post(
        "/api/v1/admin-applications", headers=student, json=payload
    )
    assert created.status_code == 201

    duplicate = client.post(
        "/api/v1/admin-applications", headers=student, json=payload
    )
    assert duplicate.status_code == 400

    forbidden = client.get("/api/v1/admin/applications", headers=student)
    assert forbidden.status_code == 403

    listing = client.get("/api/v1/admin/applications", headers=admin)
    assert listing.status_code == 200
    assert listing.json()["data"]["total"] == 1
    assert listing.json()["data"]["list"][0]["applicant_student_id"] == "20260001"


def test_approve_promotes_user(client, db, student, admin):
    application_id = client.post(
        "/api/v1/admin-applications",
        headers=student,
        json={"reason": "希望参与平台运营，每周可在线十小时"},
    ).json()["data"]["application_id"]

    approved = client.put(
        f"/api/v1/admin/applications/{application_id}",
        headers=admin,
        json={"status": 1, "review_note": "同意"},
    )
    assert approved.status_code == 200

    me = client.get("/api/v1/auth/me", headers=student)
    assert me.json()["data"]["role"] == 1

    reapply = client.post(
        "/api/v1/admin-applications",
        headers=student,
        json={"reason": "已经是管理员再次申请测试"},
    )
    assert reapply.status_code == 400


def test_regular_admin_cannot_review(client, make_user, auth):
    make_user("moderator", role=1)
    moderator = auth("moderator")

    assert client.get("/api/v1/admin/items/pending", headers=moderator).status_code == 200
    assert client.get("/api/v1/admin/applications", headers=moderator).status_code == 403


def test_rejection_cooldown(client, db, other_student, admin):
    payload = {"reason": "希望参与平台运营，每周可在线十小时"}
    application_id = client.post(
        "/api/v1/admin-applications", headers=other_student, json=payload
    ).json()["data"]["application_id"]

    rejected = client.put(
        f"/api/v1/admin/applications/{application_id}",
        headers=admin,
        json={"status": 2, "review_note": "在线时长不足"},
    )
    assert rejected.status_code == 200

    too_early = client.post(
        "/api/v1/admin-applications", headers=other_student, json=payload
    )
    assert too_early.status_code == 400

    application = db.scalar(
        select(AdminApplication).where(AdminApplication.id == application_id)
    )
    application.reviewed_at = datetime.now() - timedelta(days=4)
    db.commit()

    retry = client.post(
        "/api/v1/admin-applications", headers=other_student, json=payload
    )
    assert retry.status_code == 201


def test_application_validation(client, make_user, auth):
    make_user("20260011")

    short = client.post(
        "/api/v1/admin-applications",
        headers=auth("20260011"),
        json={"reason": "太短"},
    )
    assert short.status_code == 422

    anonymous = client.post(
        "/api/v1/admin-applications",
        json={"reason": "未登录提交管理员申请的测试"},
    )
    assert anonymous.status_code == 401
