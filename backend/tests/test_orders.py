from sqlalchemy import select

from app.models.item import Item
from app.models.order import Order
from app.models.user import User
from tests.utils import approve_item, create_item


def _user_id(db, student_id: str) -> int:
    return db.scalar(select(User.id).where(User.student_id == student_id))


def test_order_flow_and_permissions(
    client, db, student, other_student, make_user, auth, admin
):
    make_user("20260003")
    third = auth("20260003")
    item_id = create_item(client, student)
    approve_item(client, admin, item_id)

    own = client.post(
        "/api/v1/orders", headers=student, json={"item_id": item_id}
    )
    assert own.status_code == 400

    created = client.post(
        "/api/v1/orders", headers=other_student, json={"item_id": item_id}
    )
    assert created.status_code == 201
    order_id = created.json()["data"]["order_id"]

    duplicate = client.post(
        "/api/v1/orders", headers=third, json={"item_id": item_id}
    )
    assert duplicate.status_code == 400

    buyer_confirm = client.put(
        f"/api/v1/orders/{order_id}/status",
        headers=other_student,
        json={"status": 1},
    )
    assert buyer_confirm.status_code == 403

    seller_confirm = client.put(
        f"/api/v1/orders/{order_id}/status",
        headers=student,
        json={"status": 1},
    )
    assert seller_confirm.status_code == 200

    completed = client.put(
        f"/api/v1/orders/{order_id}/status",
        headers=other_student,
        json={"status": 2},
    )
    assert completed.status_code == 200

    db.expire_all()
    assert db.get(Item, item_id).status == 3
    assert client.get("/api/v1/items").json()["data"]["total"] == 0

    cancel_after_complete = client.put(
        f"/api/v1/orders/{order_id}/status",
        headers=student,
        json={"status": 3},
    )
    assert cancel_after_complete.status_code == 400


def test_cancel_frees_item_for_new_order(
    client, student, other_student, make_user, auth, admin
):
    make_user("20260003")
    third = auth("20260003")
    item_id = create_item(client, student)
    approve_item(client, admin, item_id)

    order_id = client.post(
        "/api/v1/orders", headers=other_student, json={"item_id": item_id}
    ).json()["data"]["order_id"]

    cancelled = client.put(
        f"/api/v1/orders/{order_id}/status",
        headers=other_student,
        json={"status": 3},
    )
    assert cancelled.status_code == 200

    new_order = client.post(
        "/api/v1/orders", headers=third, json={"item_id": item_id}
    )
    assert new_order.status_code == 201


def test_want_buy_reverses_buyer_and_seller(
    client, db, student, other_student, admin
):
    make_user_id = _user_id(db, "20260001")
    item_id = create_item(
        client, student, title="求购教材", type=2, price=None
    )
    approve_item(client, admin, item_id)

    order_id = client.post(
        "/api/v1/orders", headers=other_student, json={"item_id": item_id}
    ).json()["data"]["order_id"]

    db.rollback()
    order = db.get(Order, order_id)
    assert order.buyer_id == make_user_id
    assert order.seller_id == _user_id(db, "20260002")

    owner_confirm = client.put(
        f"/api/v1/orders/{order_id}/status",
        headers=student,
        json={"status": 1},
    )
    assert owner_confirm.status_code == 403

    seller_confirm = client.put(
        f"/api/v1/orders/{order_id}/status",
        headers=other_student,
        json={"status": 1},
    )
    assert seller_confirm.status_code == 200


def test_order_access_and_authentication(
    client, student, other_student, make_user, auth, admin
):
    make_user("20260003")
    third = auth("20260003")
    item_id = create_item(client, student)
    approve_item(client, admin, item_id)

    order_id = client.post(
        "/api/v1/orders", headers=other_student, json={"item_id": item_id}
    ).json()["data"]["order_id"]

    outsider = client.put(
        f"/api/v1/orders/{order_id}/status",
        headers=third,
        json={"status": 1},
    )
    assert outsider.status_code == 403

    anonymous = client.post("/api/v1/orders", json={"item_id": item_id})
    assert anonymous.status_code == 401
