import re
from typing import Tuple, Optional


def validate_string(
        value: str,
        field_name: str,
        min_length: int = 1,
        max_length: int = 200
) -> Tuple[bool, Optional[str]]:
    """Универсальная проверка строки"""
    if not value or not isinstance(value, str):
        return False, f"{field_name} обязательно"

    value = value.strip()

    if len(value) < min_length:
        return False, f"{field_name} должно быть не менее {min_length} символов"

    if len(value) > max_length:
        return False, f"{field_name} не должно превышать {max_length} символов"

    return True, None


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Проверка корректности email"""
    if not email or not isinstance(email, str):
        return False, "Email обязателен"

    email = email.strip()

    if len(email) > 120:
        return False, "Email слишком длинный"

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Некорректный формат email"

    return True, None

def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """Проверка сложности пароля"""
    if not password or not isinstance(password, str):
        return False, "Пароль обязателен"

    if len(password) < 6:
        return False, "Пароль должен быть не менее 6 символов"

    if len(password) > 128:
        return False, "Пароль слишком длинный"

    # Проверка на наличие хотя бы одной буквы
    if not re.search(r'[a-zA-Z]', password):
        return False, "Пароль должен содержать хотя бы одну букву"

    # Проверка на наличие хотя бы одной цифры
    if not re.search(r'\d', password):
        return False, "Пароль должен содержать хотя бы одну цифру"

    return True, None


def validate_integer(
        value: int,
        field_name: str,
        min_value: int = None,
        max_value: int = None
) -> Tuple[bool, Optional[str]]:
    """Универсальная проверка числа"""
    if value is None:
        return False, f"{field_name} обязательно"

    if not isinstance(value, int):
        return False, f"{field_name} должно быть числом"

    if min_value is not None and value < min_value:
        return False, f"{field_name} не может быть меньше {min_value}"

    if max_value is not None and value > max_value:
        return False, f"{field_name} не может быть больше {max_value}"

    return True, None