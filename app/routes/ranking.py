from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from flasgger import swag_from

from app.services.ranking_service import RankingService

ranking_bp = Blueprint('ranking', __name__, url_prefix='/contests/<int:contest_id>/ranking')


@ranking_bp.route('', methods=['GET'])
@jwt_required(optional=True)
@swag_from('../specs/swagger/ranking/get.yml')
def get_contest_ranking(contest_id: int):
    """Получение итогового рейтинга команд (с пагинацией)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_order = request.args.get('sort', 'desc')

    result = RankingService.get_ranking(contest_id, page, per_page, sort_order)

    return jsonify({
        "status": "success",
        **result
    }), 200
