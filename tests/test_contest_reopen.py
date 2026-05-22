"""
Тесты эндпоинта reopen и сопутствующей логики завершения после переоткрытия.
"""
from tests.helpers import bearer, login_token, register_success


def _setup(client, *, suffix):
    """Создаёт организатора, конкурс, команду, критерий, одного эксперта"""
    register_success(client, username=f"org_{suffix}", email=f"org_{suffix}@ex.com",
                     password="secret12", role="organizer")
    org_h = bearer(login_token(client, f"org_{suffix}@ex.com", "secret12"))

    contest_id = client.post(
        "/api/contests", json={"name": f"C_{suffix}", "description": ""},
        headers=org_h
    ).get_json()["contest"]["id"]

    team_id = client.post(
        f"/api/contests/{contest_id}/teams",
        json={"name": "Team", "description": ""}, headers=org_h
    ).get_json()["team"]["id"]

    crit_id = client.post(
        f"/api/contests/{contest_id}/criteria",
        json={"name": "Qu", "max_score": 10}, headers=org_h
    ).get_json()["criterion"]["id"]

    key = client.post(
        f"/api/experts/contests/{contest_id}/access-key/generate", headers=org_h
    ).get_json()["access_key"]

    register_success(client, username=f"exp_{suffix}", email=f"exp_{suffix}@ex.com",
                     password="secret12", role="expert")
    exp_h = bearer(login_token(client, f"exp_{suffix}@ex.com", "secret12"))
    join = client.post(f"/api/experts/contests/{contest_id}/join",
                       json={"access_key": key}, headers=exp_h)
    assert join.status_code == 201

    return contest_id, team_id, crit_id, org_h, exp_h


def _grade(client, headers, *, team_id, crit_id, value=8):
    return client.post("/api/grades",
                       json={"team_id": team_id, "criterion_id": crit_id, "value": value},
                       headers=headers)


def _contest(client, contest_id):
    return client.get(f"/api/contests/{contest_id}").get_json()["contest"]


# ---------------------------------------------------------------------------
# Базовый сценарий reopen
# ---------------------------------------------------------------------------

def test_reopen_allows_grade_edit(client):
    """После reopen эксперт снова может редактировать оценку"""
    contest_id, team_id, crit_id, org_h, exp_h = _setup(client, suffix="ro1")

    # Выставляем оценку → конкурс автозавершается
    r = _grade(client, exp_h, team_id=team_id, crit_id=crit_id, value=5)
    assert r.status_code == 201
    grade_id = r.get_json()["grade"]["id"]
    assert _contest(client, contest_id)["is_finished"] is True

    # Организатор переоткрывает
    reopen = client.post(f"/api/contests/{contest_id}/reopen", headers=org_h)
    assert reopen.status_code == 200, reopen.get_data(as_text=True)
    data = reopen.get_json()["contest"]
    assert data["is_finished"] is False
    assert data["is_reopened"] is True

    # Эксперт редактирует оценку - теперь это должно работать
    edit = client.put(f"/api/grades/{grade_id}", json={"value": 9}, headers=exp_h)
    assert edit.status_code == 200, edit.get_data(as_text=True)
    assert edit.get_json()["grade"]["value"] == 9


def test_reopen_disables_auto_finish_by_votes(client):
    """После reopen конкурс НЕ закрывается автоматически — нужен ручной finalize."""
    contest_id, team_id, crit_id, org_h, exp_h = _setup(client, suffix="ro2")

    # Выставляем оценку → автозавершение
    _grade(client, exp_h, team_id=team_id, crit_id=crit_id, value=7)
    assert _contest(client, contest_id)["is_finished"] is True

    # Переоткрываем
    client.post(f"/api/contests/{contest_id}/reopen", headers=org_h)
    assert _contest(client, contest_id)["is_finished"] is False

    # При запросе конкурса _check_and_update_status НЕ должен его закрыть
    # (is_reopened=True блокирует автозавершение по голосам)
    assert _contest(client, contest_id)["is_finished"] is False, (
        "Конкурс закрылся автоматически после reopen — это неверно!"
    )


def test_reopen_then_finalize_closes_contest(client):
    """После reopen организатор может закрыть конкурс через finalize."""
    contest_id, team_id, crit_id, org_h, exp_h = _setup(client, suffix="ro3")

    # Голосуем → автозавершение
    _grade(client, exp_h, team_id=team_id, crit_id=crit_id, value=6)
    assert _contest(client, contest_id)["is_finished"] is True

    # Переоткрываем
    client.post(f"/api/contests/{contest_id}/reopen", headers=org_h)

    # Вручную завершаем
    fin = client.post(f"/api/contests/{contest_id}/finalize", headers=org_h)
    assert fin.status_code == 200, fin.get_data(as_text=True)
    data = fin.get_json()["contest"]
    assert data["is_finished"] is True
    assert data["is_reopened"] is False  # флаг сброшен


def test_reopen_then_finalize_blocks_edit(client):
    """После reopen + finalize оценки снова заблокированы"""
    contest_id, team_id, crit_id, org_h, exp_h = _setup(client, suffix="ro4")

    r = _grade(client, exp_h, team_id=team_id, crit_id=crit_id, value=4)
    grade_id = r.get_json()["grade"]["id"]

    # reopen → редактируем → finalize
    client.post(f"/api/contests/{contest_id}/reopen", headers=org_h)
    client.put(f"/api/grades/{grade_id}", json={"value": 8}, headers=exp_h)
    client.post(f"/api/contests/{contest_id}/finalize", headers=org_h)

    # Теперь редактирование должно быть снова заблокировано
    block = client.put(f"/api/grades/{grade_id}", json={"value": 2}, headers=exp_h)
    assert block.status_code == 403, (
        f"Ожидался 403 после finalize, получен {block.status_code}"
    )


def test_reopen_not_finished_contest_returns_conflict(client):
    """Нельзя переоткрыть конкурс, который ещё не завершён"""
    contest_id, _, _, org_h, _ = _setup(client, suffix="ro5")

    r = client.post(f"/api/contests/{contest_id}/reopen", headers=org_h)
    assert r.status_code == 409, (
        f"Ожидался 409 (не завершён), получен {r.status_code}"
    )


def test_reopen_by_non_organizer_returns_403(client):
    """Только организатор может переоткрыть конкурс"""
    contest_id, team_id, crit_id, org_h, exp_h = _setup(client, suffix="ro6")

    # Завершаем конкурс вручную
    client.post(f"/api/contests/{contest_id}/finalize", headers=org_h)
    assert _contest(client, contest_id)["is_finished"] is True

    # Эксперт пытается переоткрыть → 403
    r = client.post(f"/api/contests/{contest_id}/reopen", headers=exp_h)
    assert r.status_code == 403, (
        f"Ожидался 403 (не организатор), получен {r.status_code}"
    )


def test_reopen_with_past_end_date_ignores_auto_finish(client):
    """
    Если у конкурса есть дата окончания в прошлом, и он переоткрыт,
    он НЕ должен автоматически закрываться по дате.
    """
    # Создаём конкурс с датой в прошлом
    past = "2000-01-01T00:00:00"
    
    register_success(client, username="org_ro7", email="org_ro7@ex.com", password="secret12", role="organizer")
    org_h = bearer(login_token(client, "org_ro7@ex.com", "secret12"))

    contest_id = client.post(
        "/api/contests", json={"name": "C_ro7", "description": "", "end_date": past},
        headers=org_h
    ).get_json()["contest"]["id"]

    # Проверяем, что конкурс сразу завершён (так как дата в прошлом)
    assert _contest(client, contest_id)["is_finished"] is True

    # Переоткрываем
    r = client.post(f"/api/contests/{contest_id}/reopen", headers=org_h)
    assert r.status_code == 200

    # Проверяем, что он не закрылся снова при следующем обращении к API
    assert _contest(client, contest_id)["is_finished"] is False
