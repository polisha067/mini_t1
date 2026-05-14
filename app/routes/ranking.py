from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from flasgger import swag_from

from app.extensions import db
from app.models.team import Team
from app.models.grade import Grade
from app.models.contest import Contest
from app.utils.errors import NotFoundError

ranking_bp = Blueprint('ranking', __name__, url_prefix='/contests/<int:contest_id>/ranking')


def _get_contest_or_404(contest_id: int) -> Contest:
    """Получить конкурс или выбросить NotFoundError"""
    contest = db.session.get(Contest, contest_id)
    if not contest:
        raise NotFoundError(f"Конкурс с id={contest_id} не найден")
    return contest


@ranking_bp.route('', methods=['GET'])
@jwt_required(optional=True)
@swag_from('../specs/swagger/ranking/get.yml')
def get_contest_ranking(contest_id: int):
    """Получение итогового рейтинга команд (с пагинацией)"""

    _get_contest_or_404(contest_id)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = min(per_page, 100)

    sort_order = request.args.get('sort', 'desc')

    has_grades = db.session.query(Grade.id).join(
        Team, Grade.team_id == Team.id
    ).filter(Team.contest_id == contest_id).first() is not None

    if not has_grades:
        teams_query = Team.query.filter_by(contest_id=contest_id).order_by(Team.name.asc())
        pagination = teams_query.paginate(page=page, per_page=per_page, error_out=False)

        ranking = []
        start_rank = (page - 1) * per_page + 1
        for idx, team in enumerate(pagination.items, start=start_rank):
            ranking.append({
                "rank": idx,
                "team_id": team.id,
                "team_name": team.name,
                "total_score": 0.0,
                "grades_count": 0
            })

        return jsonify({
            "status": "success",
            "contest_id": contest_id,
            "ranking": ranking,
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            }
        }), 200

    # Подзапрос: среднее по каждому (команда, критерий)
    # group_by по criterion_id гарантирует, что среднее считается отдельно по каждому критерию
    subquery = (
        db.session.query(
            Team.id.label('team_id'),
            Team.name.label('team_name'),
            func.avg(Grade.value).label('avg_score'),
        )
        .outerjoin(Grade, Grade.team_id == Team.id)
        .filter(Team.contest_id == contest_id)
        .group_by(Team.id, Team.name, Grade.criterion_id)
        .subquery()
    )

    # Внешний запрос: суммируем средние по всем критериям для каждой команды
    query = db.session.query(
        subquery.c.team_id,
        subquery.c.team_name,
        func.coalesce(func.sum(subquery.c.avg_score), 0).label('total_score'),
    ).group_by(
        subquery.c.team_id,
        subquery.c.team_name
    )

    if sort_order == 'desc':
        query = query.order_by(func.sum(subquery.c.avg_score).desc())
    else:
        query = query.order_by(func.sum(subquery.c.avg_score).asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Считаем количество оценок для каждой команды (отдельным запросом)
    grades_count_map = dict(
        db.session.query(Grade.team_id, func.count(Grade.id))
        .join(Team, Grade.team_id == Team.id)
        .filter(Team.contest_id == contest_id)
        .group_by(Grade.team_id)
        .all()
    )

    ranking = []
    start_rank = (page - 1) * per_page + 1

    for idx, row in enumerate(pagination.items, start=start_rank):
        ranking.append({
            "rank": idx,
            "team_id": row.team_id,
            "team_name": row.team_name,
            "total_score": round(float(row.total_score), 2),
            "grades_count": grades_count_map.get(row.team_id, 0)
        })

    return jsonify({
        "status": "success",
        "contest_id": contest_id,
        "ranking": ranking,
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }
    }), 200
