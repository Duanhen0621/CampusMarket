from sqlalchemy import select

from app.models.user import User
from tests.utils import approve_item, create_item


def _user_id(db, student_id: str) -> int:
    return db.scalar(select(User.id).where(User.student_id == student_id))


def test_report_item_validation(client, student, other_student, admin):
    item_id = create_item(client, student)
    approve_item(client, admin, item_id)

    created = client.post(
        "/api/v1/reports",
        headers=other_student,
        json={
            "target_type": 1,
            "target_id": item_id,
            "reason": "商品描述与实际不符",
        },
    )
    assert created.status_code == 201

    duplicate = client.post(
        "/api/v1/reports",
        headers=other_student,
        json={
            "target_type": 1,
            "target_id": item_id,
            "reason": "重复举报",
        },
    )
    assert duplicate.status_code == 400

    own_item = client.post(
        "/api/v1/reports",
        headers=student,
        json={
            "target_type": 1,
            "target_id": item_id,
            "reason": "举报自己的商品",
        },
    )
    assert own_item.status_code == 400

    missing = client.post(
        "/api/v1/reports",
        headers=other_student,
        json={"target_type": 1, "target_id": 9999, "reason": "不存在"},
    )
    assert missing.status_code == 404


def test_report_user_and_my_reports(
    client, db, student, other_student, admin
):
    target_user_id = _user_id(db, "20260001")
    reporter_user_id = _user_id(db, "20260002")

    created = client.post(
        "/api/v1/reports",
        headers=other_student,
        json={
            "target_type": 2,
            "target_id": target_user_id,
            "reason": "沟通态度恶劣",
        },
    )
    assert created.status_code == 201

    self_report = client.post(
        "/api/v1/reports",
        headers=other_student,
        json={
            "target_type": 2,
            "target_id": reporter_user_id,
            "reason": "举报自己",
        },
    )
    assert self_report.status_code == 400

    my_reports = client.get("/api/v1/reports/my", headers=other_student)
    assert my_reports.status_code == 200
    first = my_reports.json()["data"]["list"][0]
    assert first["target_label"] == "用户：20260001"


def test_admin_handles_reports(client, student, other_student, admin):
    item_id = create_item(client, student)
    approve_item(client, admin, item_id)
    report_id = client.post(
        "/api/v1/reports",
        headers=other_student,
        json={
            "target_type": 1,
            "target_id": item_id,
            "reason": "疑似虚假信息",
        },
    ).json()["data"]["report_id"]

    assert (
        client.get("/api/v1/admin/reports", headers=other_student).status_code
        == 403
    )

    listing = client.get("/api/v1/admin/reports", headers=admin)
    assert listing.status_code == 200
    assert listing.json()["data"]["total"] == 1

    handled = client.put(
        f"/api/v1/admin/reports/{report_id}",
        headers=admin,
        json={"status": 1, "handle_note": "已核实"},
    )
    assert handled.status_code == 200
    assert handled.json()["data"]["status"] == 1

    handled_again = client.put(
        f"/api/v1/admin/reports/{report_id}",
        headers=admin,
        json={"status": 2, "handle_note": "重复处理"},
    )
    assert handled_again.status_code == 400

    filtered = client.get(
        "/api/v1/admin/reports", headers=admin, params={"status": 1}
    )
    assert filtered.json()["data"]["total"] == 1
