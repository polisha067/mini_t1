from typing import Tuple, Optional
import re
from app.utils.validators.common import validate_string, validate_email, validate_password


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """Проверка имени пользователя"""
    if not username or not isinstance(username, str):
        return False, "Имя пользователя обязательно"

    username = username.strip()

    if len(username) < 3:
        return False, "Имя пользователя должно быть не менее 3 символов"

    if len(username) > 64:
        return False, "Имя пользователя слишком длинное"

    # Только буквы, цифры, подчёркивания
    pattern = r'^[a-zA-Z0-9_]+$'
    if not re.match(pattern, username):
        return False, "Имя пользователя может содержать только буквы, цифры и подчёркивания"

    return True, None


def validate_user_role(role: str) -> Tuple[bool, Optional[str]]:
    """Проверка роли пользователя"""
    valid_roles = ['admin', 'organizer', 'expert', 'user']

    if not role or not isinstance(role, str):
        return False, "Роль обязательна"

    if role not in valid_roles:
        return False, f"Роль должна быть одной из: {', '.join(valid_roles)}"

    return True, None


def validate_registration_data(data: dict) -> Tuple[bool, Optional[str]]:
    """Комплексная проверка данных регистрации"""
    if not data or not isinstance(data, dict):
        return False, "Данные регистрации обязательны"

    # Проверка username
    username = data.get('username', '')
    valid, error = validate_username(username)
    if not valid:
        return False, error

    # Проверка email
    email = data.get('email', '')
    valid, error = validate_email(email)
    if not valid:
        return False, error

    # Проверка пароля
    password = data.get('password', '')
    valid, error = validate_password(password)
    if not valid:
        return False, error

    role = data.get('role')
    valid, error = validate_user_role(role)
    if not valid:
        return False, error

    return True, None


def validate_login_data(data: dict) -> Tuple[bool, Optional[str]]:
    """Проверка данных входа"""
    if not data or not isinstance(data, dict):
        return False, "Данные входа обязательны"

    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email:
        return False, "Email обязателен"

    if not password:
        return False, "Пароль обязателен"

    return True, None

