from typing import Tuple, Optional
from datetime import datetime
from app.utils.validators.common import validate_string, validate_integer

def validete_team_name(name:str) -> Tuple[bool, Optional[str]]:
    """Проверка названия команды"""
    return validate_string(name, "Название команды", min_length=2, max_length=200)

def validate_team_description(description: str) -> Tuple[bool, Optional[str]]:
    """Проверка описания команды"""
    if not description:
        return True, None  # Описание необязательно

    if len(description) > 5000:
        return False, "Описание слишком длинное (максимум 5000 символов)"

    return True, None


def validate_team_data(data: dict) -> Tuple[bool, Optional[str]]:
    """Комплексная проверка данных конкурса"""
    if not data or not isinstance(data, dict):
        return False, "Данные конкурса обязательны"

    # Название
    name = data.get('name', '')
    valid, error = validete_team_name(name)
    if not valid:
        return False, error

    # Описание
    description = data.get('description', '')
    valid, error = validate_team_description(description)
    if not valid:
        return False, error

    return True, None