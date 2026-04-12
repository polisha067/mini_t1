from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

from app.extensions import db
from app.models.contest import Contest
from app.models.criterion import Criterion
from app.models.grade import Grade
from app.utils.validators.criterion import validate_criterion_data
from app.utils.decorators.rbac import role_required
from app.utils.errors import (
    ValidationError,
    NotFoundError,
    ForbiddenError,
    BadRequestError,
)

criteria_bp = Blueprint('criteria', __name__, url_prefix='/contests/<int:contest_id>/criteria')
criteria_detail_bp = Blueprint('criteria_detail', __name__, url_prefix='/criteria')


def _get_current_user_id() -> int:
    """Получить ID текущего пользователя из JWT токена"""
    return int(get_jwt_identity())


def _get_contest_or_404(contest_id: int) -> Contest:
    """Получить конкурс или выбросить NotFoundError"""
    contest = db.session.get(Contest, contest_id)
    if not contest:
        raise NotFoundError(f"Конкурс с id={contest_id} не найден")
    return contest


def _get_criterion_or_404(criterion_id: int) -> Criterion:
    """Получить критерий или выбросить NotFoundError"""
    criterion = db.session.get(Criterion, criterion_id)
    if not criterion:
        raise NotFoundError(f"Критерий с id={criterion_id} не найден")
    return criterion


def _check_organizer_ownership(contest: Contest, user_id: int) -> None:
    """Проверить, что пользователь - владелец конкурса"""
    if contest.organizer_id != user_id:
        raise ForbiddenError("Только организатор конкурса может выполнять это действие")


@criteria_bp.route('', methods=['POST'])
@jwt_required()
@role_required('organizer')
@swag_from('../specs/swagger/criteria/create.yml')
def create_criterion(contest_id: int):
    """Создание нового критерия оценивания (только организатор конкурса)"""
    contest = _get_contest_or_404(contest_id)
    user_id = _get_current_user_id()
    _check_organizer_ownership(contest, user_id)

    data = request.get_json(silent=True)
    if not data:
        raise BadRequestError("Тело запроса должно быть в формате JSON")

    valid, error = validate_criterion_data(data)
    if not valid:
        raise ValidationError(error)

    criterion = Criterion(
        name=data['name'].strip(),
        description=data.get('description', '').strip() or None,
        max_score=data.get('max_score', 10),
        contest_id=contest_id,
    )

    try:
        db.session.add(criterion)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

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
    _get_contest_or_404(contest_id)

    query = Criterion.query.filter_by(contest_id=contest_id)
    query = query.order_by(Criterion.id.asc())

    criteria = [criterion.to_dict() for criterion in query.all()]

    return jsonify({
        "status": "success",
        "criteria": criteria,
        "total": len(criteria)
    }), 200


@criteria_detail_bp.route('/<int:criterion_id>', methods=['GET'])
@jwt_required(optional=True)
@swag_from('../specs/swagger/criteria/detail.yml')
def get_criterion(criterion_id: int):
    """Получение деталей критерия по ID"""
    criterion = _get_criterion_or_404(criterion_id)

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
    criterion = _get_criterion_or_404(criterion_id)
    contest = _get_contest_or_404(criterion.contest_id)
    user_id = _get_current_user_id()
    _check_organizer_ownership(contest, user_id)

    # Защита: нельзя менять критерий с существующими оценками
    has_grades = Grade.query.filter_by(criterion_id=criterion_id).first()
    if has_grades:
        raise ForbiddenError("Нельзя изменить критерий - уже выставлены оценки")

    data = request.get_json(silent=True)
    if not data:
        raise BadRequestError("Тело запроса должно быть в формате JSON")

    valid, error = validate_criterion_data(data)
    if not valid:
        raise ValidationError(error)

    # Обновляем только переданные поля
    if 'name' in data:
        criterion.name = data['name'].strip()
    if 'description' in data:
        criterion.description = data['description'].strip() or None
    if 'max_score' in data:
        criterion.max_score = data['max_score']

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

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
    criterion = _get_criterion_or_404(criterion_id)
    contest = _get_contest_or_404(criterion.contest_id)
    user_id = _get_current_user_id()
    _check_organizer_ownership(contest, user_id)

    try:
        db.session.delete(criterion)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({
        "status": "success",
        "message": f"Критерий '{criterion.name}' успешно удалён"
    }), 200
