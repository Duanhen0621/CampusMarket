def test_super_admin_revokes_admin(client, make_user, auth, admin):
    moderator_id = make_user("moderator", role=1)
    moderator = auth("moderator")
    assert client.get("/api/v1/admin/items/pending", headers=moderator).status_code == 200

    response = client.put(
        f"/api/v1/admin/users/{moderator_id}/role",
        headers=admin,
        json={"role": 0},
    )
    assert response.status_code == 200
    assert response.json()["data"]["role"] == 0

    assert client.get("/api/v1/admin/items/pending", headers=moderator).status_code == 403
    me = client.get("/api/v1/auth/me", headers=moderator)
    assert me.json()["data"]["role"] == 0


def test_regular_admin_cannot_revoke(client, make_user, auth):
    make_user("moderator", role=1)
    target_id = make_user("other_moderator", role=1)
    moderator = auth("moderator")

    response = client.put(
        f"/api/v1/admin/users/{target_id}/role",
        headers=moderator,
        json={"role": 0},
    )
    assert response.status_code == 403


def test_cannot_revoke_super_admin(client, make_user, admin):
    super_id = make_user("another_super", role=2)
    response = client.put(
        f"/api/v1/admin/users/{super_id}/role",
        headers=admin,
        json={"role": 0},
    )
    assert response.status_code == 400


def test_cannot_grant_admin_directly(client, make_user, admin):
    user_id = make_user("20260014")
    response = client.put(
        f"/api/v1/admin/users/{user_id}/role",
        headers=admin,
        json={"role": 1},
    )
    assert response.status_code == 400
