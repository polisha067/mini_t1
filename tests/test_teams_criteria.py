from tests.helpers import bearer, login_token, register_success


def _organizer_token_and_contest(client):
    register_success(
        client,
        username="org_tc",
        email="org_tc@example.com",
        password="secret12",
        role="organizer",
    )
    token = login_token(client, "org_tc@example.com", "secret12")
    headers = bearer(token)
    create = client.post(
        "/api/contests",
        json={"name": "Contest Teams", "description": "desc"},
        headers=headers,
    )
    assert create.status_code == 201
    return token, headers, create.get_json()["contest"]["id"]


def test_team_create_and_list(client):
    _, headers, contest_id = _organizer_token_and_contest(client)

    create_team = client.post(
        f"/api/contests/{contest_id}/teams",
        json={"name": "Alpha Team", "description": "First"},
        headers=headers,
    )
    assert create_team.status_code == 201
    team_id = create_team.get_json()["team"]["id"]

    lst = client.get(f"/api/contests/{contest_id}/teams")
    assert lst.status_code == 200
    teams = lst.get_json()["teams"]
    assert len(teams) == 1
    assert teams[0]["id"] == team_id
    assert teams[0]["name"] == "Alpha Team"


def test_team_detail_404(client):
    response = client.get("/api/teams/888888")
    assert response.status_code == 404


def test_criterion_create_and_list(client):
    _, headers, contest_id = _organizer_token_and_contest(client)

    create_cr = client.post(
        f"/api/contests/{contest_id}/criteria",
        json={"name": "Innovation", "description": "", "max_score": 10},
        headers=headers,
    )
    assert create_cr.status_code == 201

    lst = client.get(f"/api/contests/{contest_id}/criteria")
    assert lst.status_code == 200
    criteria = lst.get_json()["criteria"]
    assert len(criteria) == 1
    assert criteria[0]["name"] == "Innovation"
    assert criteria[0]["max_score"] == 10
