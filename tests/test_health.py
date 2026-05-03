def test_api_status_returns_ok(client):
    response = client.get("/api/status")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["server"] == "running"
    assert "version" in payload


def test_api_home_guest(client):
    response = client.get("/api/home")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["page"] == "home"
    assert payload["is_authenticated"] is False
    assert payload["user"] is None
