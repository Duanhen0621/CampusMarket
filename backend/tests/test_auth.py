def test_register_login_and_me(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "student_id": "20260011",
            "password": "password123",
            "nickname": "小明",
            "phone": "13800000001",
        },
    )
    assert response.status_code == 201
    assert response.json()["data"]["student_id"] == "20260011"
    assert response.json()["data"]["nickname"] == "小明"

    duplicate = client.post(
        "/api/v1/auth/register",
        json={"student_id": "20260011", "password": "password123"},
    )
    assert duplicate.status_code == 400

    wrong = client.post(
        "/api/v1/auth/login",
        json={"student_id": "20260011", "password": "wrong-password"},
    )
    assert wrong.status_code == 401

    login = client.post(
        "/api/v1/auth/login",
        json={"student_id": "20260011", "password": "password123"},
    )
    assert login.status_code == 200
    token = login.json()["data"]["access_token"]

    me = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me.status_code == 200
    assert me.json()["data"]["role"] == 0


def test_update_profile(client, student):
    response = client.put(
        "/api/v1/auth/me",
        headers=student,
        json={"nickname": "阿杰", "phone": "13900000000"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["nickname"] == "阿杰"
    assert response.json()["data"]["phone"] == "13900000000"

    me = client.get("/api/v1/auth/me", headers=student)
    assert me.json()["data"]["nickname"] == "阿杰"
    assert me.json()["data"]["phone"] == "13900000000"


def test_login_rejects_banned_user(client, make_user):
    make_user("20260012", status=0)
    response = client.post(
        "/api/v1/auth/login",
        json={"student_id": "20260012", "password": "20260012"},
    )
    assert response.status_code == 403


def test_protected_endpoint_requires_valid_token(client):
    assert client.get("/api/v1/auth/me").status_code == 401
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer bad-token"}
    )
    assert response.status_code == 401


def test_change_password(client, make_user, auth):
    make_user("20260013", password="oldpass123")
    headers = auth("20260013", "oldpass123")

    missing_old = client.put(
        "/api/v1/auth/me",
        headers=headers,
        json={"new_password": "newpass456"},
    )
    assert missing_old.status_code == 400

    wrong_old = client.put(
        "/api/v1/auth/me",
        headers=headers,
        json={"old_password": "bad-password", "new_password": "newpass456"},
    )
    assert wrong_old.status_code == 400

    changed = client.put(
        "/api/v1/auth/me",
        headers=headers,
        json={"old_password": "oldpass123", "new_password": "newpass456"},
    )
    assert changed.status_code == 200

    old_login = client.post(
        "/api/v1/auth/login",
        json={"student_id": "20260013", "password": "oldpass123"},
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/api/v1/auth/login",
        json={"student_id": "20260013", "password": "newpass456"},
    )
    assert new_login.status_code == 200
