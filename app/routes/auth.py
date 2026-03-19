from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

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

    access_token = create_access_token(identity=user.id)

    return jsonify({
        "status": "success",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200