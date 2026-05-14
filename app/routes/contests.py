from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

from app.services.contest_service import ContestService
from app.utils.decorators.rbac import role_required

contests_bp = Blueprint('contests', __name__, url_prefix='/contests')

contest_service = ContestService()


def _get_current_user_id() -> int:
    return int(get_jwt_identity())


def _parse_request_data():
    """Универсальный парсер: поддерживает JSON и multipart/form-data"""
    if request.content_type and 'multipart/form-data' in request.content_type:
        return request.form.to_dict(), request.files.get('logo')
    else:
        return request.get_json(silent=True), None


@contests_bp.route('', methods=['POST'])
@jwt_required()
@role_required('organizer')
@swag_from('../specs/swagger/contests/create.yml')
def create_contest():
    """Создание нового конкурса (только для организаторов)"""
    data, logo_file = _parse_request_data()
    user_id = _get_current_user_id()
    contest = ContestService.create(data, logo_file, user_id)

    return jsonify({
        "status": "success",
        "message": "Конкурс успешно создан",
        "contest": contest.to_dict()
    }), 201


@contests_bp.route('', methods=['GET'])
@jwt_required(optional=True)
@swag_from('../specs/swagger/contests/list.yml')
def list_contests():
    """Получение списка всех конкурсов с пагинацией"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    organizer_id = request.args.get('organizer_id', type=int)

    pagination = ContestService.get_list(page, per_page, organizer_id)
    contests = [contest.to_dict() for contest in pagination.items]

    return jsonify({
        "status": "success",
        "contests": contests,
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }
    }), 200


@contests_bp.route('/<int:contest_id>', methods=['GET'])
@jwt_required(optional=True)
@swag_from('../specs/swagger/contests/detail.yml')
def get_contest(contest_id: int):
    """Получение деталей конкурса по ID"""
    contest = ContestService.get_by_id(contest_id)

    return jsonify({
        "status": "success",
        "contest": contest.to_dict()
    }), 200


@contests_bp.route('/<int:contest_id>', methods=['PUT'])
@jwt_required()
@role_required('organizer')
@swag_from('../specs/swagger/contests/update.yml')
def update_contest(contest_id: int):
    """Обновление конкурса (только для организатора-владельца)"""
    data, logo_file = _parse_request_data()
    user_id = _get_current_user_id()
    contest = contest_service.update(contest_id, data, logo_file, user_id)

    return jsonify({
        "status": "success",
        "message": "Конкурс успешно обновлён",
        "contest": contest.to_dict()
    }), 200


@contests_bp.route('/<int:contest_id>', methods=['DELETE'])
@jwt_required()
@role_required('organizer')
@swag_from('../specs/swagger/contests/delete.yml')
def delete_contest(contest_id: int):
    """Удаление конкурса и всех связанных данных (cascade)"""
    user_id = _get_current_user_id()
    contest = contest_service.delete(contest_id, user_id)

    return jsonify({
        "status": "success",
        "message": f"Конкурс '{contest.name}' успешно удалён"
    }), 200


@contests_bp.route('/<int:contest_id>/finalize', methods=['POST'])
@jwt_required()
@role_required('organizer')
@swag_from('../specs/swagger/contests/finalize.yml')
def finalize_contest(contest_id: int):
    """Завершение голосования по конкурсу (только организатор)"""
    user_id = _get_current_user_id()
    contest = contest_service.finalize(contest_id, user_id)

    return jsonify({
        "status": "success",
        "message": f"Голосование по конкурсу '{contest.name}' завершено",
        "contest": contest.to_dict()
    }), 200


@contests_bp.route('/<int:contest_id>/voting-status', methods=['GET'])
@jwt_required()
@swag_from('../specs/swagger/contests/voting_status.yml')
def get_voting_status(contest_id: int):
    """Статус голосования по конкурсу"""
    result = ContestService.get_voting_status(contest_id)

    return jsonify({
        "status": "success",
        **result
    }), 200