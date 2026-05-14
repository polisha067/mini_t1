from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

from app.services.team_service import TeamService
from app.utils.decorators.rbac import role_required

teams_bp = Blueprint('teams', __name__, url_prefix='/contests/<int:contest_id>/teams')
teams_detail_bp = Blueprint('teams_detail', __name__, url_prefix='/teams')


def _get_current_user_id() -> int:
    return int(get_jwt_identity())


def _optional_current_user_id():
    ident = get_jwt_identity()
    if ident is None:
        return None
    try:
        return int(ident)
    except (TypeError, ValueError):
        return None


@teams_bp.route('', methods=['POST'])
@jwt_required()
@role_required('organizer')
@swag_from('../specs/swagger/teams/create.yml')
def create_team(contest_id: int):
    """Создание новой команды (только организатор может)"""
    data = request.get_json(silent=True)
    team = TeamService.create(contest_id, data)

    return jsonify({
        "status": "success",
        "message": "Команда успешно создана",
        "team": team.to_dict()
    }), 201


@teams_bp.route('', methods=['GET'])
@jwt_required(optional=True)
@swag_from('../specs/swagger/teams/list.yml')
def list_teams(contest_id: int):
    """Получение списка всех команд с пагинацией"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    viewer_id = _optional_current_user_id()
    pagination = TeamService.get_list(
        contest_id, page, per_page, viewer_user_id=viewer_id
    )
    teams = [team.to_dict() for team in pagination.items]

    return jsonify({
        "status": "success",
        "teams": teams,
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }
    }), 200


@teams_detail_bp.route('/<int:team_id>', methods=['GET'])
@jwt_required(optional=True)
@swag_from('../specs/swagger/teams/detail.yml')
def get_team(team_id: int):
    """Получение деталей команды по ID"""
    team = TeamService.get_by_id(team_id)

    return jsonify({
        "status": "success",
        "team": team.to_dict()
    }), 200


@teams_detail_bp.route('/<int:team_id>', methods=['PUT'])
@jwt_required()
@role_required('organizer')
@swag_from('../specs/swagger/teams/update.yml')
def update_team(team_id: int):
    """Обновление команды (только для организатора конкурса)"""
    data = request.get_json(silent=True)
    user_id = _get_current_user_id()
    team = TeamService.update(team_id, data, user_id)

    return jsonify({
        "status": "success",
        "message": "Команда успешно обновлена",
        "team": team.to_dict()
    }), 200


@teams_detail_bp.route('/<int:team_id>', methods=['DELETE'])
@jwt_required()
@role_required('organizer')
@swag_from('../specs/swagger/teams/delete.yml')
def delete_team(team_id: int):
    """Удаление команды и всех связанных оценок"""
    user_id = _get_current_user_id()
    team = TeamService.delete(team_id, user_id)

    return jsonify({
        "status": "success",
        "message": f"Команда '{team.name}' успешно удалена"
    }), 200