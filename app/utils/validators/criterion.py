from typing import Tuple, Optional
from app.utils.validators.common import validate_string, validate_integer


def validate_criterion_name(name: str) -> Tuple[bool, Optional[str]]:
    """Проверка названия критерия"""
    return validate_string(name, "Название критерия", min_length=2, max_length=200)


def validate_criterion_description(description: str) -> Tuple[bool, Optional[str]]:
    """Проверка описания критерия"""
    if not description:
        return True, None  # Описание необязательно

    if len(description) > 5000:
        return False, "Описание слишком длинное (максимум 5000 символов)"

    return True, None


def validate_max_score(max_score: int) -> Tuple[bool, Optional[str]]:
    """Проверка максимального балла (1-100)"""
    return validate_integer(max_score, "Максимальный балл", min_value=1, max_value=100)


def validate_criterion_data(data: dict) -> Tuple[bool, Optional[str]]:
    """Комплексная проверка данных критерия"""
    if not data or not isinstance(data, dict):
        return False, "Данные критерия обязательны"

    # Название
    name = data.get('name', '')
    valid, error = validate_criterion_name(name)
    if not valid:
        return False, error

    # Описание
    description = data.get('description', '')
    valid, error = validate_criterion_description(description)
    if not valid:
        return False, error

    # Максимальный балл
    max_score = data.get('max_score')
    if max_score is not None:
        valid, error = validate_max_score(max_score)
        if not valid:
            return False, error

    return True, None
