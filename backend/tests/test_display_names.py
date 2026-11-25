from tests.utils import approve_item, create_item


def test_display_names_across_pages(client, make_user, auth, admin):
    seller_id = make_user("20260001", nickname="阿杰")
    make_user("20260002", nickname="小满")
    seller = auth("20260001")
    buyer = auth("20260002")

    item_id = create_item(client, seller)
    approve_item(client, admin, item_id)

    detail = client.get(f"/api/v1/items/{item_id}")
    assert detail.json()["data"]["publisher_display_name"] == "阿杰"

    message = client.post(
        f"/api/v1/items/{item_id}/messages",
        headers=buyer,
        json={"content": "同学你好"},
    )
    assert message.status_code == 201
    assert message.json()["data"]["display_name"] == "小满"

    messages = client.get(f"/api/v1/items/{item_id}/messages")
    assert messages.json()["data"]["list"][0]["display_name"] == "小满"

    client.post("/api/v1/orders", headers=buyer, json={"item_id": item_id})
    orders = client.get("/api/v1/orders/my", headers=seller)
    first = orders.json()["data"]["list"][0]
    assert first["buyer_display_name"] == "小满"
    assert first["seller_display_name"] == "阿杰"

    client.post(
        "/api/v1/reports",
        headers=buyer,
        json={
            "target_type": 2,
            "target_id": seller_id,
            "reason": "举报用户显示昵称测试",
        },
    )
    reports = client.get("/api/v1/reports/my", headers=buyer)
    assert reports.json()["data"]["list"][0]["target_label"] == "用户：阿杰"


def test_application_shows_applicant_nickname(
    client, make_user, auth, admin
):
    make_user("20260001", nickname="阿杰")
    applicant = auth("20260001")

    client.post(
        "/api/v1/admin-applications",
        headers=applicant,
        json={"reason": "希望协助审核商品并处理举报，每周可在线十小时"},
    )
    listing = client.get("/api/v1/admin/applications", headers=admin)
    first = listing.json()["data"]["list"][0]
    assert first["applicant_display_name"] == "阿杰"
