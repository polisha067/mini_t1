from typing import Tuple, Optional
from app.utils.validators.common import validate_integer


def validate_grade_comment(comment: str) -> Tuple[bool, Optional[str]]:
    """Проверка комментария к оценке"""
    if not comment:
        return True, None

    if len(comment) > 3000:
        return False, "Комментарий слишком длинный (максимум 3000 символов)"

    return True, None


def validate_grade_value(value: int, max_score: int) -> Tuple[bool, Optional[str]]:
    """Проверка значения оценки (0-max_score)"""
    return validate_integer(value, "Оценка", min_value=0, max_value=max_score)


def validate_grade_data(data: dict, max_score: int) -> Tuple[bool, Optional[str]]:
    """Комплексная проверка данных оценки"""
    if not data or not isinstance(data, dict):
        return False, "Данные оценки обязательны"

    # Проверка обязательных полей
    if 'team_id' not in data:
        return False, "Поле team_id обязательно"
    if 'criterion_id' not in data:
        return False, "Поле criterion_id обязательно"
    if 'value' not in data:
        return False, "Поле value обязательно"

    # Проверка значения оценки
    value = data.get('value')
    valid, error = validate_grade_value(value, max_score)
    if not valid:
        return False, error

    # Проверка комментария
    comment = data.get('comment', '')
    valid, error = validate_grade_comment(comment)
    if not valid:
        return False, error

    return True, None
