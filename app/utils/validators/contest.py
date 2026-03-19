from typing import Tuple, Optional
from datetime import datetime
from app.utils.validators.common import validate_string, validate_integer


def validate_contest_name(name: str) -> Tuple[bool, Optional[str]]:
    """Проверка названия конкурса"""
    return validate_string(name, "Название конкурса", min_length=3, max_length=200)


def validate_contest_description(description: str) -> Tuple[bool, Optional[str]]:
    """Проверка описания конкурса"""
    if not description:
        return True, None  # Описание необязательно

    if len(description) > 5000:
        return False, "Описание слишком длинное (максимум 5000 символов)"

    return True, None


def validate_contest_dates(start_date: str, end_date: str) -> Tuple[bool, Optional[str]]:
    """Проверка дат конкурса"""
    if not start_date or not end_date:
        return True, None  # Даты необязательны

    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        if start >= end:
            return False, "Дата начала должна быть раньше даты окончания"

        return True, None
    except (ValueError, AttributeError):
        return False, "Некорректный формат даты"


def validate_contest_data(data: dict) -> Tuple[bool, Optional[str]]:
    """Комплексная проверка данных конкурса"""
    if not data or not isinstance(data, dict):
        return False, "Данные конкурса обязательны"

    # Название
    name = data.get('name', '')
    valid, error = validate_contest_name(name)
    if not valid:
        return False, error

    # Описание
    description = data.get('description', '')
    valid, error = validate_contest_description(description)
    if not valid:
        return False, error

    # Даты
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    valid, error = validate_contest_dates(start_date, end_date)
    if not valid:
        return False, error

    return True, None


def validate_score(value: int, max_score: int = 10) -> Tuple[bool, Optional[str]]:
    """Проверка оценки"""
    return validate_integer(value, "Оценка", min_value=0, max_value=max_score)