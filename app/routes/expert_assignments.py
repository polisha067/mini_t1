from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.expert_service import ExpertService

expert_bp = Blueprint('experts', __name__, url_prefix='/experts')


def _get_current_user_id() -> int:
    return int(get_jwt_identity())


@expert_bp.route('/contests/<int:contest_id>/access-key/generate', methods=['POST'])
@jwt_required()
def generate_access_key(contest_id: int):
    """Генерация ключа доступа для экспертов"""
    user_id = _get_current_user_id()
    new_key = ExpertService.generate_access_key(contest_id, user_id)

    return jsonify({"status": "success", "access_key": new_key}), 200


@expert_bp.route('/contests/<int:contest_id>/join', methods=['POST'])
@jwt_required()
def join_contest_by_key(contest_id: int):
    """Присоединение эксперта к конкурсу по ключу"""
    data = request.get_json(silent=True)
    user_id = _get_current_user_id()
    is_new, message = ExpertService.join_contest(contest_id, data, user_id)

    return jsonify({
        "status": "success",
        "message": message
    }), 201 if is_new else 200


@expert_bp.route('/me/contests', methods=['GET'])
@jwt_required()
def get_expert_contests():
    """Получение списка конкурсов эксперта"""
    expert_id = _get_current_user_id()
    contests = ExpertService.get_expert_contests(expert_id)

    return jsonify({
        "status": "success",
        "contests": [c.to_dict() for c in contests]
    }), 200


@expert_bp.route('/contests/<int:contest_id>/experts', methods=['GET'])
@jwt_required()
def get_contest_experts(contest_id: int):
    """Получение списка экспертов конкурса"""
    experts = ExpertService.get_contest_experts(contest_id)

    return jsonify({
        "status": "success",
        "experts": [e.to_dict() for e in experts]
    }), 200
