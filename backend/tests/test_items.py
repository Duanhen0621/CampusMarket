import io
from pathlib import Path

from PIL import Image

from app.core.config import settings
from tests.utils import approve_item, create_item, reject_item


def test_publish_requires_price_for_sale(client, student):
    response = client.post(
        "/api/v1/items",
        headers=student,
        json={"title": "无价格商品", "type": 1, "image_urls": []},
    )
    assert response.status_code == 400


def test_publish_audit_and_detail_flow(client, student, admin):
    item_id = create_item(client, student, title="九成新自行车")

    public_list = client.get("/api/v1/items")
    assert public_list.json()["data"]["total"] == 0

    my_items = client.get("/api/v1/items/my", headers=student)
    assert my_items.json()["data"]["list"][0]["status"] == 0

    pending = client.get("/api/v1/admin/items/pending", headers=admin)
    assert pending.json()["data"]["total"] == 1

    approve_item(client, admin, item_id)

    public_list = client.get("/api/v1/items")
    assert public_list.json()["data"]["total"] == 1
    assert client.get(f"/api/v1/items/{item_id}").status_code == 200


def test_reject_reason_and_resubmit(client, student, admin):
    item_id = create_item(client, student)

    reject_item(client, admin, item_id, "图片不清晰")

    assert client.get(f"/api/v1/items/{item_id}").status_code == 404
    my_items = client.get("/api/v1/items/my", headers=student)
    first = my_items.json()["data"]["list"][0]
    assert first["status"] == 2
    assert first["reject_reason"] == "图片不清晰"

    edit_data = client.get(f"/api/v1/items/{item_id}/edit", headers=student)
    assert edit_data.status_code == 200

    updated = client.put(
        f"/api/v1/items/{item_id}",
        headers=student,
        json={"title": "修改后的商品"},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["status"] == 0
    assert updated.json()["data"]["reject_reason"] is None

    approve_item(client, admin, item_id)
    detail = client.get(f"/api/v1/items/{item_id}")
    assert detail.json()["data"]["title"] == "修改后的商品"


def test_edit_permissions(client, student, other_student):
    item_id = create_item(client, student)

    assert client.get(f"/api/v1/items/{item_id}/edit").status_code == 401
    assert (
        client.get(
            f"/api/v1/items/{item_id}/edit", headers=other_student
        ).status_code
        == 403
    )
    assert (
        client.put(
            f"/api/v1/items/{item_id}",
            headers=other_student,
            json={"title": "越权修改"},
        ).status_code
        == 403
    )


def test_off_shelf_hides_item(client, student, admin):
    item_id = create_item(client, student)
    approve_item(client, admin, item_id)

    response = client.delete(f"/api/v1/items/{item_id}", headers=student)
    assert response.status_code == 200
    assert client.get("/api/v1/items").json()["data"]["total"] == 0

    my_items = client.get("/api/v1/items/my", headers=student)
    assert my_items.json()["data"]["list"][0]["status"] == 3


def test_search_and_type_filter(client, student, admin):
    bike = create_item(client, student, title="九成新山地自行车")
    want = create_item(
        client, student, title="求购宿舍冰箱", type=2, price=None
    )
    approve_item(client, admin, bike)
    approve_item(client, admin, want)

    keyword = client.get("/api/v1/items", params={"keyword": "自行车"})
    assert keyword.json()["data"]["total"] == 1

    type_filter = client.get("/api/v1/items", params={"type": 2})
    assert type_filter.json()["data"]["total"] == 1


def test_upload_image(client, student):
    buffer = io.BytesIO()
    Image.new("RGB", (120, 90), (90, 140, 200)).save(buffer, "PNG")
    buffer.seek(0)

    response = client.post(
        "/api/v1/uploads/image",
        headers=student,
        files={"file": ("test.png", buffer, "image/png")},
    )
    assert response.status_code == 201
    url = response.json()["data"]["url"]
    assert url.startswith("/uploads/") and url.endswith(".jpg")

    saved = Path(settings.upload_path) / url.split("/")[-1]
    assert saved.exists()

    invalid = client.post(
        "/api/v1/uploads/image",
        headers=student,
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    assert invalid.status_code == 400

    assert (
        client.post(
            "/api/v1/uploads/image",
            files={"file": ("test.png", b"", "image/png")},
        ).status_code
        == 401
    )
