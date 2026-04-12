from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

from app.extensions import db
from app.models.grade import Grade
from app.models.team import Team
from app.models.criterion import Criterion
from app.models.contest import Contest
from app.utils.validators.grade import validate_grade_data
from app.utils.decorators.rbac import role_required
from app.utils.errors import (
    ValidationError,
    NotFoundError,
    ForbiddenError,
    BadRequestError,
)

grades_by_expert_bp = Blueprint('grades_by_expert', __name__, url_prefix='/experts/<int:expert_id>/grades')

grades_by_team_bp = Blueprint('grades_by_team', __name__, url_prefix='/teams/<int:team_id>/grades')

grades_bp = Blueprint('grades', __name__, url_prefix='/grades')


def _get_current_user_id() -> int:
    """Получить ID текущего пользователя из JWT токена"""
    return int(get_jwt_identity())


def _get_grade_or_404(grade_id: int) -> Grade:
    """Получить оценку или выбросить NotFoundError"""
    grade = db.session.get(Grade, grade_id)
    if not grade:
        raise NotFoundError(f"Оценка с id={grade_id} не найдена")
    return grade


def _get_criterion_or_404(criterion_id: int) -> Criterion:
    """Получить критерий или выбросить NotFoundError"""
    criterion = db.session.get(Criterion, criterion_id)
    if not criterion:
        raise NotFoundError(f"Критерий с id={criterion_id} не найден")
    return criterion


def _get_team_or_404(team_id: int) -> Team:
    """Получить команду или выбросить NotFoundError"""
    team = db.session.get(Team, team_id)
    if not team:
        raise NotFoundError(f"Команда с id={team_id} не найдена")
    return team


def _check_expert_ownership(grade: Grade, user_id: int) -> None:
    """Проверить, что пользователь — владелец оценки"""
    if grade.expert_id != user_id:
        raise ForbiddenError("Эксперт может редактировать только свои оценки")


@grades_bp.route('', methods=['POST'])
@jwt_required()
@role_required('expert')
@swag_from('../specs/swagger/grades/create.yml')
def create_grade():
    """Выставление оценки (только эксперт конкурса)"""

    data = request.get_json(silent=True)
    if not data:
        raise BadRequestError("Тело запроса должно быть в формате JSON")

    team_id = data.get('team_id')
    criterion_id = data.get('criterion_id')

    if not team_id or not criterion_id or 'value' not in data:
        raise ValidationError("Поля team_id, criterion_id и value обязательны")

    team = _get_team_or_404(team_id)
    criterion = _get_criterion_or_404(criterion_id)

    if criterion.contest_id != team.contest_id:
        raise ValidationError("Критерий не принадлежит данной команде")

    # Проверка: голосование завершено?
    contest = db.session.get(Contest, team.contest_id)
    if contest and contest.is_finished:
        raise ForbiddenError("Голосование по этому конкурсу завершено")

    # Валидация через валидатор (max_score берём из модели критерия)
    valid, error = validate_grade_data(data, criterion.max_score)
    if not valid:
        raise ValidationError(error)

    # expert_id из JWT — эксперт не может подделать чужую оценку
    expert_id = _get_current_user_id()

    grade = Grade(
        expert_id=expert_id,
        team_id=team_id,
        criterion_id=criterion_id,
        value=data['value'],
        comment=data.get('comment', '').strip() or None,
    )

    try:
        db.session.add(grade)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

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

    _get_team_or_404(team_id)

    query = Grade.query.filter_by(team_id=team_id)
    query = query.order_by(Grade.id.asc())

    grades = [grade.to_dict() for grade in query.all()]

    return jsonify({
        "status": "success",
        "grades": grades,
        "total": len(grades)
    }), 200


@grades_by_expert_bp.route('', methods=['GET'])
@jwt_required()
@swag_from('../specs/swagger/grades/expert_grades.yml')
def list_expert_grades(expert_id: int):
    """Получение всех оценок эксперта"""

    current_user_id = _get_current_user_id()

    if current_user_id != expert_id:
        raise ForbiddenError("Вы можете просматривать только свои оценки")

    query = Grade.query.filter_by(expert_id=expert_id)
    query = query.order_by(Grade.created_at.desc())

    grades = [grade.to_dict() for grade in query.all()]

    return jsonify({
        "status": "success",
        "grades": grades,
        "total": len(grades)
    }), 200


@grades_bp.route('/<int:grade_id>', methods=['PUT'])
@jwt_required()
@role_required('expert')
@swag_from('../specs/swagger/grades/update.yml')
def update_grade(grade_id: int):
    """Редактирование оценки (только владелец)"""
    grade = _get_grade_or_404(grade_id)

    user_id = _get_current_user_id()
    _check_expert_ownership(grade, user_id)

    # Проверка: голосование завершено?
    team = _get_team_or_404(grade.team_id)
    contest = db.session.get(Contest, team.contest_id)
    if contest and contest.is_finished:
        raise ForbiddenError("Голосование по этому конкурсу завершено")

    data = request.get_json(silent=True)
    if not data:
        raise BadRequestError("Тело запроса должно быть в формате JSON")

    if 'value' in data:
        criterion = _get_criterion_or_404(grade.criterion_id)
        valid, error = validate_grade_data({'value': data['value']}, criterion.max_score)
        if not valid:
            raise ValidationError(error)
        grade.value = data['value']

    if 'comment' in data:
        comment = data['comment']
        if comment and len(comment) > 3000:
            raise ValidationError("Комментарий слишком длинный (максимум 3000 символов)")
        grade.comment = comment.strip() or None

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

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
    grade = _get_grade_or_404(grade_id)

    current_user_id = _get_current_user_id()
    _check_expert_ownership(grade, current_user_id)

    try:
        db.session.delete(grade)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({
        "status": "success",
        "message": f"Оценка {grade.value} успешно удалена"
    }), 200
