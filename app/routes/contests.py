import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

from app.extensions import db
from app.models.contest import Contest
from app.models.team import Team
from app.models.criterion import Criterion
from app.models.grade import Grade
from app.models.contest_expert import ContestExpert
from app.utils.validators.contest import validate_contest_data
from app.utils.decorators.rbac import role_required
from app.utils.errors import (
    ValidationError,
    NotFoundError,
    ForbiddenError,
    BadRequestError,
    ConflictError,
)
# Утилита для безопасной загрузки файлов (создайте её по инструкции ниже)
from app.utils.file_upload import save_uploaded_file

contests_bp = Blueprint('contests', __name__, url_prefix='/contests')


def _get_current_user_id() -> int:
    """Получить ID текущего пользователя из JWT токена"""
    return int(get_jwt_identity())


def _get_contest_or_404(contest_id: int) -> Contest:
    """Получить конкурс или выбросить NotFoundError"""
    contest = db.session.get(Contest, contest_id)
    if not contest:
        raise NotFoundError(f"Конкурс с id={contest_id} не найден")
    return contest


def _check_organizer_ownership(contest: Contest, user_id: int) -> None:
    """Проверить, что пользователь - владелец конкурса"""
    if contest.organizer_id != user_id:
        raise ForbiddenError("Только организатор конкурса может выполнять это действие")


def _parse_request_data():
    """
    Универсальный парсер: поддерживает JSON и multipart/form-data.
    Возвращает кортеж (data_dict, logo_file_or_None)
    """
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
    if not data:
        raise BadRequestError("Тело запроса должно быть в формате JSON или multipart/form-data")

    valid, error = validate_contest_data(data)
    if not valid:
        raise ValidationError(error)

    user_id = _get_current_user_id()
    logo_path = None

    # 1. Обработка загруженного файла
    if logo_file and logo_file.filename:
        try:
            logo_path = save_uploaded_file(logo_file, folder='logos')
        except ValueError as e:
            raise ValidationError(str(e))
    # 2. Fallback для старых клиентов (передача строки URL/пути)
    elif data.get('logo_path'):
        logo_path = data.get('logo_path')

    contest = Contest(
        name=data['name'].strip(),
        description=data.get('description', '').strip() or None,
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        logo_path=logo_path,
        organizer_id=user_id,
    )

    try:
        db.session.add(contest)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

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
    per_page = min(per_page, 100)  # Максимум 100 на страницу

    # Фильтрация по organizer_id (опционально)
    organizer_id = request.args.get('organizer_id', type=int)

    query = Contest.query
    if organizer_id:
        query = query.filter_by(organizer_id=organizer_id)

    query = query.order_by(Contest.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

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
    contest = _get_contest_or_404(contest_id)
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
    contest = _get_contest_or_404(contest_id)
    user_id = _get_current_user_id()
    _check_organizer_ownership(contest, user_id)

    data, logo_file = _parse_request_data()
    if not data:
        raise BadRequestError("Тело запроса должно быть в формате JSON или multipart/form-data")

    valid, error = validate_contest_data(data)
    if not valid:
        raise ValidationError(error)

    # Обновляем текстовые/датные поля
    if 'name' in data:
        contest.name = data['name'].strip()
    if 'description' in data:
        contest.description = data['description'].strip() or None
    if 'start_date' in data:
        contest.start_date = data['start_date']
    if 'end_date' in data:
        contest.end_date = data['end_date']

    # Обработка логотипа
    if logo_file and logo_file.filename:
        # Удаляем старый физический файл, если он есть
        if contest.logo_path:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            old_path = os.path.join(upload_folder, contest.logo_path)
            if os.path.exists(old_path):
                os.remove(old_path)
        # Сохраняем новый
        try:
            contest.logo_path = save_uploaded_file(logo_file, folder='logos')
        except ValueError as e:
            raise ValidationError(str(e))
    elif 'logo_path' in data:
        contest.logo_path = data.get('logo_path')

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

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
    contest = _get_contest_or_404(contest_id)
    user_id = _get_current_user_id()
    _check_organizer_ownership(contest, user_id)

    if contest.is_finished:
        raise ForbiddenError("Нельзя удалить завершённый конкурс")

    try:
        db.session.delete(contest)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

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
    contest = _get_contest_or_404(contest_id)
    user_id = _get_current_user_id()
    _check_organizer_ownership(contest, user_id)

    if contest.is_finished:
        raise ConflictError("Голосование уже завершено")

    contest.is_finished = True

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

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
    contest = _get_contest_or_404(contest_id)

    if contest.is_finished:
        return jsonify({
            "status": "success",
            "contest_id": contest_id,
            "is_finished": True,
            "message": "Голосование завершено"
        }), 200

    # Считаем ожидаемое количество оценок
    teams_count = Team.query.filter_by(contest_id=contest_id).count()
    criteria_count = Criterion.query.filter_by(contest_id=contest_id).count()
    experts_count = ContestExpert.query.filter_by(contest_id=contest_id).count()

    expected_grades = teams_count * criteria_count * experts_count
    actual_grades = Grade.query.join(Team).filter(Team.contest_id == contest_id).count()

    # Статус
    if expected_grades == 0:
        voting_status = "not_started"
        message = "Нет данных для голосования"
    elif actual_grades == 0:
        voting_status = "not_started"
        message = "Никто не выставил оценок"
    elif actual_grades == expected_grades:
        voting_status = "all_votes_cast"
        message = f"Все эксперты выставили оценки ({actual_grades}/{expected_grades})"
    else:
        voting_status = "in_progress"
        missing = expected_grades - actual_grades
        message = f"Голосование в процессе: {actual_grades}/{expected_grades} оценок, не хватает {missing}"

    return jsonify({
        "status": "success",
        "contest_id": contest_id,
        "is_finished": False,
        "voting_status": voting_status,
        "expected_grades": expected_grades,
        "actual_grades": actual_grades,
        "missing_grades": max(0, expected_grades - actual_grades),
        "teams_count": teams_count,
        "criteria_count": criteria_count,
        "experts_count": experts_count,
        "message": message
    }), 200