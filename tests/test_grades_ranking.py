from tests.helpers import bearer, login_token, register_success


def _full_setup(client):
    register_success(
        client,
        username="org_gr",
        email="org_gr@example.com",
        password="secret12",
        role="organizer",
    )
    org_headers = bearer(login_token(client, "org_gr@example.com", "secret12"))
    contest = client.post(
        "/api/contests",
        json={"name": "Grade Contest", "description": "grading"},
        headers=org_headers,
    ).get_json()
    contest_id = contest["contest"]["id"]

    team = client.post(
        f"/api/contests/{contest_id}/teams",
        json={"name": "Team X", "description": ""},
        headers=org_headers,
    ).get_json()
    team_id = team["team"]["id"]

    crit = client.post(
        f"/api/contests/{contest_id}/criteria",
        json={"name": "Quality", "max_score": 10},
        headers=org_headers,
    ).get_json()
    criterion_id = crit["criterion"]["id"]

    key = client.post(
        f"/api/experts/contests/{contest_id}/access-key/generate",
        headers=org_headers,
    ).get_json()["access_key"]

    register_success(
        client,
        username="exp_gr",
        email="exp_gr@example.com",
        password="secret12",
        role="expert",
    )
    expert_headers = bearer(login_token(client, "exp_gr@example.com", "secret12"))

    join = client.post(
        f"/api/experts/contests/{contest_id}/join",
        json={"access_key": key},
        headers=expert_headers,
    )
    assert join.status_code == 201

    return contest_id, team_id, criterion_id, expert_headers


def test_expert_create_grade_and_list_by_team(client):
    contest_id, team_id, criterion_id, eh = _full_setup(client)

    grade_post = client.post(
        "/api/grades",
        json={
            "team_id": team_id,
            "criterion_id": criterion_id,
            "value": 8,
            "comment": "Solid work",
        },
        headers=eh,
    )
    assert grade_post.status_code == 201
    g = grade_post.get_json()["grade"]
    assert g["value"] == 8

    listed = client.get(f"/api/teams/{team_id}/grades")
    assert listed.status_code == 200
    grades = listed.get_json()["grades"]
    assert len(grades) == 1
    assert grades[0]["value"] == 8


def test_ranking_includes_team_after_grade(client):
    contest_id, team_id, criterion_id, eh = _full_setup(client)
    client.post(
        "/api/grades",
        json={"team_id": team_id, "criterion_id": criterion_id, "value": 7},
        headers=eh,
    )

    ranking = client.get(f"/api/contests/{contest_id}/ranking")
    assert ranking.status_code == 200
    rows = ranking.get_json()["ranking"]
    assert len(rows) >= 1
    top = next(r for r in rows if r["team_id"] == team_id)
    assert top["total_score"] >= 7.0
    assert top["grades_count"] == 1
