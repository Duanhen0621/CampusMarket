def create_item(client, headers, **overrides) -> int:
    payload = {
        "title": "测试商品",
        "description": "测试描述",
        "type": 1,
        "price": 100,
        "image_urls": [],
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()["data"]["item_id"]


def approve_item(client, admin_headers, item_id: int) -> None:
    response = client.put(
        f"/api/v1/admin/items/{item_id}/audit",
        headers=admin_headers,
        json={"status": 1},
    )
    assert response.status_code == 200, response.text


def reject_item(client, admin_headers, item_id: int, reason: str) -> None:
    response = client.put(
        f"/api/v1/admin/items/{item_id}/audit",
        headers=admin_headers,
        json={"status": 2, "reason": reason},
    )
    assert response.status_code == 200, response.text
