from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from flasgger import swag_from

from app.extensions import db
from app.models.team import Team
from app.models.grade import Grade
from app.models.contest import Contest
from app.utils.errors import NotFoundError

ranking_bp = Blueprint('ranking', __name__,url_prefix='/contests/<int:contest_id>/ranking')

def _get_contest_or_404(contest_id: int) -> Contest:
    """Получить конкурс или выбросить NotFoundError"""
    contest = db.session.get(Contest, contest_id)
    if not contest:
        raise NotFoundError(f"Конкурс с id={contest_id} не найден")
    return contest

@ranking_bp.route('', methods = ['GET'])
@jwt_required(optional=True)
@swag_from('../specs/swagger/ranking/get.yml')
def get_contest_ranking(contest_id):
    """Получение итогового рейтинга команд (с пагинацией)"""

    _get_contest_or_404(contest_id)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = min(per_page, 100)

    sort_order = request.args.get('sort', 'desc')

    order_func = func.avg(Grade.value).desc() if sort_order == 'desc' else func.avg(Grade.value).asc()

    query = db.session.query(
        Team.id.label('team_id'),
        Team.name.label('team_name'),
        func.avg(Grade.value).label('total_score'),
        func.count(Grade.id).label('grades_count')
    ).outerjoin(
        Grade, Grade.team_id == Team.id
    ).filter(
        Team.contest_id == contest_id
    ).group_by(
        Team.id, Team.name
    ).order_by(order_func)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    ranking = []
    # Место команды на каждой новой странице, чтобы не начиналась с 1 каждый раз
    start_rank = (page - 1) * per_page + 1

    for idx, row in enumerate(pagination.items, start=start_rank):
        ranking.append({
            "rank": idx,
            "team_id": row.team_id,
            "team_name": row.team_name,
            "total_score": round(float(row.total_score or 0), 2),
            "grades_count": row.grades_count
        })

    return jsonify({
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