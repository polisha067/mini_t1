from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

from app.services.grade_service import GradeService
from app.utils.decorators.rbac import role_required

grades_by_expert_bp = Blueprint('grades_by_expert', __name__, url_prefix='/experts/<int:expert_id>/grades')
grades_by_team_bp = Blueprint('grades_by_team', __name__, url_prefix='/teams/<int:team_id>/grades')
grades_bp = Blueprint('grades', __name__, url_prefix='/grades')


def _get_current_user_id() -> int:
    return int(get_jwt_identity())


@grades_bp.route('', methods=['POST'])
@jwt_required()
@role_required('expert')
@swag_from('../specs/swagger/grades/create.yml')
def create_grade():
    """Выставление оценки (только эксперт конкурса)"""
    data = request.get_json(silent=True)
    expert_id = _get_current_user_id()
    grade = GradeService.create(data, expert_id)

    return jsonify({
        "status": "success",
        "message": "Оценка успешно выставлена",
        "grade": grade.to_dict()
    }), 201


@grades_by_team_bp.route('', methods=['GET'])
@jwt_required(optional=True)
@swag_from('../specs/swagger/grades/list.yml')
def list_grades(team_id: int):
    """Получение всех оценок команды"""
    grades = GradeService.get_list_by_team(team_id)

    return jsonify({
        "status": "success",
        "grades": [g.to_dict() for g in grades],
        "total": len(grades)
    }), 200


@grades_by_expert_bp.route('', methods=['GET'])
@jwt_required()
@swag_from('../specs/swagger/grades/expert_grades.yml')
def list_expert_grades(expert_id: int):
    """Получение всех оценок эксперта"""
    current_user_id = _get_current_user_id()
    grades = GradeService.get_list_by_expert(expert_id, current_user_id)

    return jsonify({
        "status": "success",
        "grades": [g.to_dict() for g in grades],
        "total": len(grades)
    }), 200


@grades_bp.route('/<int:grade_id>', methods=['PUT'])
@jwt_required()
@role_required('expert')
@swag_from('../specs/swagger/grades/update.yml')
def update_grade(grade_id: int):
    """Редактирование оценки (только владелец)"""
    data = request.get_json(silent=True)
    user_id = _get_current_user_id()
    grade = GradeService.update(grade_id, data, user_id)

    return jsonify({
        "status": "success",
        "message": "Оценка успешно обновлена",
        "grade": grade.to_dict()
    }), 200


@grades_bp.route('/<int:grade_id>', methods=['DELETE'])
@jwt_required()
@role_required('expert')
@swag_from('../specs/swagger/grades/delete.yml')
def delete_grade(grade_id: int):
    """Удаление оценки (только владелец)"""
    user_id = _get_current_user_id()
    grade = GradeService.delete(grade_id, user_id)

    return jsonify({
        "status": "success",
        "message": f"Оценка {grade.value} успешно удалена"
    }), 200
