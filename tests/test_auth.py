def test_register_and_login_returns_token(client):
    reg = client.post(
        "/api/auth/register",
        json={
            "username": "test_org",
            "email": "test_org@example.com",
            "password": "secret12",
            "role": "organizer",
        },
    )
    assert reg.status_code == 201
    reg_body = reg.get_json()
    assert reg_body["status"] == "success"
    assert reg_body["user"]["username"] == "test_org"

    login = client.post(
        "/api/auth/login",
        json={
            "email": "test_org@example.com",
            "password": "secret12",
        },
    )
    assert login.status_code == 200
    login_body = login.get_json()
    token = login_body["access_token"]
    assert isinstance(token, str) and token

    me = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200
    me_body = me.get_json()
    assert me_body["user"]["email"] == "test_org@example.com"


def test_login_wrong_password_is_unauthorized(client):
    client.post(
        "/api/auth/register",
        json={
            "username": "judge_one",
            "email": "judge@example.com",
            "password": "correct1",
            "role": "expert",
        },
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "judge@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
