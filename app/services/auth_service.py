import hashlib

from flask_jwt_extended import create_access_token, create_refresh_token

from app.extensions import db
from app.models.user import User
from app.utils.validators import validate_registration_data, validate_login_data
from app.utils.validators.common import validate_password
from app.utils.errors import (
    ValidationError,
    ConflictError,
    UnauthorizedError,
    BadRequestError,
)


class AuthService:
    """Сервис аутентификации и управления пользователями"""

    @staticmethod
    def get_redirect_url_for_role(role: str) -> str:
        return '/home'

    @staticmethod
    def register(data: dict) -> User:
        """Регистрация нового пользователя"""
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

        return user

    @staticmethod
    def login(data: dict) -> tuple[User, str, str]:
        """Аутентификация. Возвращает (user, access_token, refresh_token)"""
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
        access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=str(user.id))

        return user, access_token, refresh_token

    @staticmethod
    def get_user_by_id(user_id: int) -> User:
        """Получить пользователя по ID"""
        user = db.session.get(User, user_id)
        if not user:
            raise UnauthorizedError("Пользователь не найден")
        return user

    @staticmethod
    def refresh_access_token(identity: str) -> tuple[User, str]:
        """Обновление access токена. Возвращает (user, new_access_token)"""
        user = db.session.get(User, int(identity))
        if not user:
            raise UnauthorizedError("Пользователь не найден")

        additional_claims = {'role': user.role}
        new_access_token = create_access_token(
            identity=identity,
            additional_claims=additional_claims
        )

        return user, new_access_token

    @staticmethod
    def forgot_password(data: dict) -> tuple[bool, str | None]:
        """Запрос на сброс пароля. Возвращает (user_found, raw_token_or_None)"""
        if not data:
            raise BadRequestError("Тело запроса должно быть в формате JSON")

        email = data.get('email', '').strip().lower()
        if not email:
            raise ValidationError("Поле email обязательно")

        user = User.query.filter_by(email=email).first()

        if user:
            raw_token = user.generate_reset_token()
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise
            return True, raw_token

        return False, None

    @staticmethod
    def reset_password(data: dict) -> None:
        """Сброс пароля по токену"""
        if not data:
            raise BadRequestError("Тело запроса должно быть в формате JSON")

        token = data.get('token', '').strip()
        new_password = data.get('new_password', '')

        if not token:
            raise ValidationError("Поле token обязательно")
        if not new_password:
            raise ValidationError("Поле new_password обязательно")

        valid, error = validate_password(new_password)
        if not valid:
            raise ValidationError(error)

        token_hash = hashlib.sha256(token.encode()).hexdigest()
        user = User.query.filter_by(reset_token_hash=token_hash).first()

        if not user or not user.verify_reset_token(token):
            raise UnauthorizedError("Токен недействителен или истёк")

        user.set_password(new_password)
        user.clear_reset_token()

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
