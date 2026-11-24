from tests.utils import approve_item, create_item


def test_messages_flow(client, student, other_student, admin):
    item_id = create_item(client, student)
    approve_item(client, admin, item_id)

    created = client.post(
        f"/api/v1/items/{item_id}/messages",
        headers=other_student,
        json={"content": "同学你好，商品还在吗？"},
    )
    assert created.status_code == 201
    assert created.json()["data"]["student_id"] == "20260002"

    listing = client.get(f"/api/v1/items/{item_id}/messages")
    assert listing.status_code == 200
    assert listing.json()["data"]["total"] == 1

    blank = client.post(
        f"/api/v1/items/{item_id}/messages",
        headers=other_student,
        json={"content": "   "},
    )
    assert blank.status_code == 400

    anonymous = client.post(
        f"/api/v1/items/{item_id}/messages",
        json={"content": "未登录留言"},
    )
    assert anonymous.status_code == 401

    missing = client.get("/api/v1/items/9999/messages")
    assert missing.status_code == 404


def test_favorites_flow(client, student, other_student, admin):
    item_id = create_item(client, student)
    approve_item(client, admin, item_id)

    assert (
        client.post(
            f"/api/v1/items/{item_id}/favorite", headers=other_student
        ).status_code
        == 201
    )

    duplicate = client.post(
        f"/api/v1/items/{item_id}/favorite", headers=other_student
    )
    assert duplicate.status_code == 400

    check = client.get(
        f"/api/v1/favorites/check/{item_id}", headers=other_student
    )
    assert check.json()["data"]["favorited"] is True

    my_favorites = client.get("/api/v1/favorites/my", headers=other_student)
    assert my_favorites.json()["data"]["total"] == 1

    removed = client.delete(
        f"/api/v1/items/{item_id}/favorite", headers=other_student
    )
    assert removed.status_code == 200

    check = client.get(
        f"/api/v1/favorites/check/{item_id}", headers=other_student
    )
    assert check.json()["data"]["favorited"] is False

    missing = client.delete(
        f"/api/v1/items/{item_id}/favorite", headers=other_student
    )
    assert missing.status_code == 404


def test_interactions_require_approved_item(client, student, other_student):
    item_id = create_item(client, student)

    assert (
        client.post(
            f"/api/v1/items/{item_id}/messages",
            headers=other_student,
            json={"content": "未审核商品留言"},
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/v1/items/{item_id}/favorite", headers=other_student
        ).status_code
        == 404
    )
