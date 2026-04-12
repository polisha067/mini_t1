from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

from app.extensions import db
from app.models.contest import Contest
from app.models.user import User
from app.models.contest_expert import ContestExpert
from app.utils.validators.expert_assignment import validate_expert_assignment_data
from app.utils.decorators.rbac import role_required
from app.utils.errors import (
    ValidationError,
    NotFoundError,
    ForbiddenError,
    BadRequestError,
    ConflictError,
)

expert_bp = Blueprint('expert_assignments', __name__)


def _get_current_user_id() -> int:
    """Получить ID текущего пользователя из JWT токена"""
    return int(get_jwt_identity())


def _get_contest_or_404(contest_id: int) -> Contest:
    """Получить конкурс или выбросить NotFoundError"""
    contest = db.session.get(Contest, contest_id)
    if not contest:
        raise NotFoundError(f"Конкурс с id={contest_id} не найден")
    return contest


def _get_user_or_404(user_id: int) -> User:
    """Получить пользователя или выбросить NotFoundError"""
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError(f"Пользователь с id={user_id} не найден")
    return user


def _check_organizer_ownership(contest: Contest, user_id: int) -> None:
    """Проверить, что пользователь — владелец конкурса"""
    if contest.organizer_id != user_id:
        raise ForbiddenError("Только организатор конкурса может выполнять это действие")


@expert_bp.route('/contests/<int:contest_id>/experts', methods=['POST'])
@jwt_required()
@role_required('organizer')
@swag_from('../specs/swagger/expert_assignments/assign.yml')
def assign_expert(contest_id: int):
    """Назначение эксперта на конкурс (только организатор конкурса)"""
    contest = _get_contest_or_404(contest_id)
    user_id = _get_current_user_id()
    _check_organizer_ownership(contest, user_id)

    data = request.get_json(silent=True)
    if not data:
        raise BadRequestError("Тело запроса должно быть в формате JSON")

    valid, error = validate_expert_assignment_data(data)
    if not valid:
        raise ValidationError(error)

    expert_id = data['expert_id']
    expert = _get_user_or_404(expert_id)

    # Проверяем, что пользователь - эксперт
    if expert.role != 'expert':
        raise ValidationError(f"Пользователь '{expert.username}' не является экспертом (роль: {expert.role})")

    # Проверяем, не назначен ли уже
    existing = ContestExpert.query.filter_by(
        contest_id=contest_id,
        user_id=expert_id
    ).first()

    if existing:
        raise ConflictError(f"Эксперт '{expert.username}' уже назначен на этот конкурс")

    assignment = ContestExpert(
        contest_id=contest_id,
        user_id=expert_id,
    )

    try:
        db.session.add(assignment)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({
        "status": "success",
        "message": f"Эксперт '{expert.username}' назначен на конкурс '{contest.name}'",
        "assignment": {
            "id": assignment.id,
            "contest_id": assignment.contest_id,
            "expert_id": assignment.user_id,
            "expert_name": expert.username,
            "assigned_at": assignment.assigned_at.isoformat() if assignment.assigned_at else None
        }
    }), 201


@expert_bp.route('/contests/<int:contest_id>/experts', methods=['GET'])
@jwt_required()
@swag_from('../specs/swagger/expert_assignments/list.yml')
def list_contest_experts(contest_id: int):
    """Получение списка экспертов, назначенных на конкурс"""
    _get_contest_or_404(contest_id)

    assignments = ContestExpert.query.filter_by(contest_id=contest_id).all()

    experts = []
    for assignment in assignments:
        expert = db.session.get(User, assignment.user_id)
        if expert:
            experts.append({
                "id": expert.id,
                "username": expert.username,
                "email": expert.email,
                "assigned_at": assignment.assigned_at.isoformat() if assignment.assigned_at else None
            })

    return jsonify({
        "status": "success",
        "contest_id": contest_id,
        "experts": experts,
        "total": len(experts)
    }), 200


@expert_bp.route('/experts/me/contests', methods=['GET'])
@jwt_required()
@role_required('expert')
@swag_from('../specs/swagger/expert_assignments/my_contests.yml')
def get_expert_contests():
    """Получение списка конкурсов, на которые назначен текущий эксперт"""
    expert_id = _get_current_user_id()

    assignments = ContestExpert.query.filter_by(user_id=expert_id).all()

    contests = []
    for assignment in assignments:
        contest = db.session.get(Contest, assignment.contest_id)
        if contest:
            contests.append({
                "id": contest.id,
                "name": contest.name,
                "description": contest.description,
                "start_date": contest.start_date.isoformat() if contest.start_date else None,
                "end_date": contest.end_date.isoformat() if contest.end_date else None,
                "assigned_at": assignment.assigned_at.isoformat() if assignment.assigned_at else None
            })

    return jsonify({
        "status": "success",
        "expert_id": expert_id,
        "contests": contests,
        "total": len(contests)
    }), 200


@expert_bp.route('/contests/<int:contest_id>/experts/<int:expert_id>', methods=['DELETE'])
@jwt_required()
@role_required('organizer')
@swag_from('../specs/swagger/expert_assignments/remove.yml')
def remove_expert(contest_id: int, expert_id: int):
    """Удаление эксперта из конкурса (только организатор конкурса)"""
    contest = _get_contest_or_404(contest_id)
    user_id = _get_current_user_id()
    _check_organizer_ownership(contest, user_id)

    assignment = ContestExpert.query.filter_by(
        contest_id=contest_id,
        user_id=expert_id
    ).first()

    if not assignment:
        raise NotFoundError(f"Эксперт с id={expert_id} не назначен на этот конкурс")

    try:
        db.session.delete(assignment)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({
        "status": "success",
        "message": f"Эксперт с id={expert_id} удалён из конкурса"
    }), 200
