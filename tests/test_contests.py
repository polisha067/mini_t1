from tests.helpers import bearer, login_token, register_success


def test_list_contests_empty_without_auth(client):
    response = client.get("/api/contests")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "success"
    assert body["contests"] == []
    assert body["pagination"]["total"] == 0


def test_organizer_creates_contest_and_get_detail(client):
    register_success(
        client,
        username="org_c",
        email="org_c@example.com",
        password="secret12",
        role="organizer",
    )
    token = login_token(client, "org_c@example.com", "secret12")
    headers = bearer(token)

    create = client.post(
        "/api/contests",
        json={"name": "Spring Hack", "description": "Annual event"},
        headers=headers,
    )
    assert create.status_code == 201
    contest_id = create.get_json()["contest"]["id"]

    detail = client.get(f"/api/contests/{contest_id}", headers=headers)
    assert detail.status_code == 200
    c = detail.get_json()["contest"]
    assert c["name"] == "Spring Hack"
    assert c["organizer_id"] is not None


def test_contest_detail_404(client):
    response = client.get("/api/contests/999999")
    assert response.status_code == 404


def test_expert_cannot_create_contest(client):
    register_success(
        client,
        username="exp_c",
        email="exp_c@example.com",
        password="secret12",
        role="expert",
    )
    token = login_token(client, "exp_c@example.com", "secret12")

    response = client.post(
        "/api/contests",
        json={"name": "Bad Create", "description": ""},
        headers=bearer(token),
    )
    assert response.status_code == 403


def test_organizer_voting_status_empty_contest(client):
    register_success(
        client,
        username="org_v",
        email="org_v@example.com",
        password="secret12",
        role="organizer",
    )
    token = login_token(client, "org_v@example.com", "secret12")
    headers = bearer(token)

    create = client.post(
        "/api/contests",
        json={"name": "Vote Demo", "description": ""},
        headers=headers,
    )
    contest_id = create.get_json()["contest"]["id"]

    response = client.get(
        f"/api/contests/{contest_id}/voting-status",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["is_finished"] is False
    assert data["voting_status"] == "not_started"
