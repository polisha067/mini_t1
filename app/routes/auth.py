from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt

from app.extensions import db
from app.models.user import User
from app.models.contest import Contest
from app.utils.validators import validate_registration_data, validate_login_data
from app.utils.errors import (
    ValidationError,
    ConflictError,
    UnauthorizedError,
    BadRequestError,
)
from app.utils.decorators import role_required, admin_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Регистрация нового пользователя"""
    data = request.get_json(silent=True)
    if not data:
        raise BadRequestError("Тело запроса должно быть в формате JSON")

    valid, error = validate_registration_data(data)
    if not valid:
        raise ValidationError(error)

    username = data['username'].strip()
    email = data['email'].strip().lower()
    password = data['password']
    role = data['role']

    if User.query.filter_by(email=email).first():
        raise ConflictError("Пользователь с таким email уже существует")

    if User.query.filter_by(username=username).first():
        raise ConflictError("Пользователь с таким именем уже существует")

    user = User(username=username, email=email, role=role)
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({
        "status": "success",
        "message": "Пользователь успешно зарегистрирован",
        "user": user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Аутентификация пользователя и выдача JWT токена"""
    data = request.get_json(silent=True)
    if not data:
        raise BadRequestError("Тело запроса должно быть в формате JSON")

    valid, error = validate_login_data(data)
    if not valid:
        raise ValidationError(error)

    email = data['email'].strip().lower()
    password = data['password']

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        raise UnauthorizedError("Неверный email или пароль")

    additional_claims = {'role': user.role}
    access_token = create_access_token(identity=user.id, additional_claims=additional_claims)

    return jsonify({
        "status": "success",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """Защищённый эндпоинт: данные текущего пользователя"""
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if not user:
        raise UnauthorizedError("Пользователь не найден")

    return jsonify({
        "status": "success",
        "user": user.to_dict()
    }), 200


@auth_bp.route('/organizer', methods=['GET'])
@role_required('organizer')
def organizer_panel():
    """Эндпоинт только для организаторов: сводка по своим конкурсам"""
    user_id = int(get_jwt_identity())
    contests_count = Contest.query.filter_by(organizer_id=user_id).count()

    return jsonify({
        "status": "success",
        "message": "Панель организатора",
        "data": {
            "contests_count": contests_count,
            "features": [
                "create_contest",
                "manage_teams",
                "manage_criteria",
                "assign_experts",
                "view_ranking",
            ],
        },
    }), 200


@auth_bp.route('/admin', methods=['GET'])
@admin_required
def admin_panel():
    """Эндпоинт только для администраторов"""
    return jsonify({
        "status": "success",
        "message": "Панель администратора",
        "data": {
            "users_count": User.query.count(),
            "admin_features": ["user_management", "system_settings", "audit_logs"]
        }
    }), 200


@auth_bp.route('/expert', methods=['GET'])
@role_required('expert')
def expert_panel():
    """Эндпоинт только для экспертов"""
    return jsonify({
        "status": "success",
        "message": "Панель эксперта",
        "data": {
            "features": ["contest_evaluation", "grade_submission", "results_review"]
        }
    }), 200