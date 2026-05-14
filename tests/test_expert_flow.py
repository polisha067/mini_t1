from tests.helpers import bearer, login_token, register_success


def _setup_contest_with_key(client):
    register_success(
        client,
        username="org_ek",
        email="org_ek@example.com",
        password="secret12",
        role="organizer",
    )
    org_token = login_token(client, "org_ek@example.com", "secret12")
    org_headers = bearer(org_token)
    contest = client.post(
        "/api/contests",
        json={"name": "Key Contest", "description": "join test"},
        headers=org_headers,
    ).get_json()
    contest_id = contest["contest"]["id"]

    key_resp = client.post(
        f"/api/experts/contests/{contest_id}/access-key/generate",
        headers=org_headers,
    )
    assert key_resp.status_code == 200
    access_key = key_resp.get_json()["access_key"]

    register_success(
        client,
        username="expert_ek",
        email="expert_ek@example.com",
        password="secret12",
        role="expert",
    )
    expert_token = login_token(client, "expert_ek@example.com", "secret12")

    return contest_id, access_key, org_headers, expert_token


def test_expert_join_with_key_lists_expert(client):
    contest_id, access_key, org_headers, expert_token = _setup_contest_with_key(client)
    eh = bearer(expert_token)

    join = client.post(
        f"/api/experts/contests/{contest_id}/join",
        json={"access_key": access_key},
        headers=eh,
    )
    assert join.status_code == 201

    experts_resp = client.get(
        f"/api/experts/contests/{contest_id}/experts",
        headers=eh,
    )
    assert experts_resp.status_code == 200
    experts = experts_resp.get_json()["experts"]
    assert len(experts) == 1
    assert experts[0]["username"] == "expert_ek"

    my = client.get("/api/experts/me/contests", headers=eh)
    assert my.status_code == 200
    contests = my.get_json()["contests"]
    assert len(contests) == 1
    assert contests[0]["id"] == contest_id


def test_expert_join_wrong_key_400(client):
    contest_id, _, _, expert_token = _setup_contest_with_key(client)
    join = client.post(
        f"/api/experts/contests/{contest_id}/join",
        json={"access_key": "wrong-key-xxxx"},
        headers=bearer(expert_token),
    )
    assert join.status_code == 422


def test_organizer_cannot_join_as_expert_endpoint(client):
    contest_id, access_key, org_headers, _ = _setup_contest_with_key(client)
    resp = client.post(
        f"/api/experts/contests/{contest_id}/join",
        json={"access_key": access_key},
        headers=org_headers,
    )
    assert resp.status_code == 403
