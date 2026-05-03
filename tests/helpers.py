def bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def register_success(client, *, username: str, email: str, password: str, role: str) -> dict:
    response = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "role": role,
        },
    )
    assert response.status_code == 201, response.get_data(as_text=True)
    return response.get_json()


def login_token(client, email: str, password: str) -> str:
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.get_data(as_text=True)
    return response.get_json()["access_token"]
