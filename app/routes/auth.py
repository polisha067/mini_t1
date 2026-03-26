from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from app.extensions import db
from app.models.user import User
from app.utils.validators import validate_registration_data, validate_login_data
from app.utils.errors import (
    ValidationError,
    ConflictError,
    UnauthorizedError,
    BadRequestError,
)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def get_redirect_url_for_role(role: str) -> str:
    """
    Все пользователи перенаправляются на /home полсле аторизации или регистрации
    """
    return '/home'

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
        "user": user.to_dict(),
        "redirect_url": get_redirect_url_for_role(user.role)
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
        "user": user.to_dict(),
        "redirect_url": get_redirect_url_for_role(user.role)
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


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Выход из системы (на клиенте нужно удалить токен)"""
    return jsonify({
        "status": "success",
        "message": "Выход выполнен успешно"
    }), 200