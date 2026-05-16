from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

from app.services.criterion_service import CriterionService
from app.utils.decorators.rbac import role_required

criteria_bp = Blueprint('criteria', __name__, url_prefix='/contests/<int:contest_id>/criteria')
criteria_detail_bp = Blueprint('criteria_detail', __name__, url_prefix='/criteria')


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


@criteria_bp.route('', methods=['POST'])
@jwt_required()
@role_required('organizer')
@swag_from('../specs/swagger/criteria/create.yml')
def create_criterion(contest_id: int):
    """Создание нового критерия оценивания (только организатор конкурса)"""
    data = request.get_json(silent=True)
    user_id = _get_current_user_id()
    criterion = CriterionService.create(contest_id, data, user_id)

    return jsonify({
        "status": "success",
        "message": "Критерий успешно создан",
        "criterion": criterion.to_dict()
    }), 201


@criteria_bp.route('', methods=['GET'])
@jwt_required(optional=True)
@swag_from('../specs/swagger/criteria/list.yml')
def list_criteria(contest_id: int):
    """Получение списка всех критериев конкурса"""
    viewer_id = _optional_current_user_id()
    criteria = CriterionService.get_list(contest_id, viewer_user_id=viewer_id)

    return jsonify({
        "status": "success",
        "criteria": [c.to_dict() for c in criteria],
        "total": len(criteria)
    }), 200


@criteria_detail_bp.route('/<int:criterion_id>', methods=['GET'])
@jwt_required(optional=True)
@swag_from('../specs/swagger/criteria/detail.yml')
def get_criterion(criterion_id: int):
    """Получение деталей критерия по ID"""
    criterion = CriterionService.get_by_id(criterion_id)

    return jsonify({
        "status": "success",
        "criterion": criterion.to_dict()
    }), 200


@criteria_detail_bp.route('/<int:criterion_id>', methods=['PUT'])
@jwt_required()
@role_required('organizer')
@swag_from('../specs/swagger/criteria/update.yml')
def update_criterion(criterion_id: int):
    """Обновление критерия (только организатор конкурса)"""
    data = request.get_json(silent=True)
    user_id = _get_current_user_id()
    criterion = CriterionService.update(criterion_id, data, user_id)

    return jsonify({
        "status": "success",
        "message": "Критерий успешно обновлён",
        "criterion": criterion.to_dict()
    }), 200


@criteria_detail_bp.route('/<int:criterion_id>', methods=['DELETE'])
@jwt_required()
@role_required('organizer')
@swag_from('../specs/swagger/criteria/delete.yml')
def delete_criterion(criterion_id: int):
    """Удаление критерия и всех связанных оценок (cascade)"""
    user_id = _get_current_user_id()
    criterion = CriterionService.delete(criterion_id, user_id)

    return jsonify({
        "status": "success",
        "message": f"Критерий '{criterion.name}' успешно удалён"
    }), 200
