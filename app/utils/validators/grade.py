from typing import Tuple, Optional
from app.utils.validators.common import validate_integer
from app.extensions import db
from app.models.criterion import Criterion

def validate_grade_comment(comment:str)->Tuple[bool, Optional[str]]:
    """Проверка комментарий к оценке"""
    if not comment:
        return True, None
    
    if len(comment) > 3000:
        return False, "Комментарий слишком длинный (максимум 3000 символов)"
    return True, None

def validate_grade_value(value: int , max_score: int) ->Tuple[bool, Optional[str]]:
    """Проверка значения оценки (1-max_score)"""
    return validate_integer(value, "Оценка", min_value=0, max_value=max_score)

def _get_max_score_for_criterion(criterion_id: int) -> Optional[int]:
    """Получить max_score для критерия (для использования при валидации)"""
    criterion = db.session.get(Criterion, criterion_id)
    if criterion:
        return criterion.max_score
    return None

def validate_grade_data(data:dict) -> Tuple[bool, Optional[str]]:
    """Комплексная проверка данных оценки"""
    if not data or not isinstance(data, dict):
        return False, "Данные оценки обязательны"
    
    comment = data.get('comment', '')
    valid, error = validate_grade_comment(comment)
    if not valid:
        return False, error
    
    value = data.get('value')
    criterion_id = data.get('criterion_id')
    max_score = _get_max_score_for_criterion(criterion_id)

    valid, error = validate_grade_value(value, max_score)
    if not valid:
        return False, error
    
    return True, None
