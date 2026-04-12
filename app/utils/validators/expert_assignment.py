from typing import Tuple, Optional


def validate_expert_assignment_data(data: dict) -> Tuple[bool, Optional[str]]:
    """Проверка данных для назначения эксперта на конкурс"""
    if not data or not isinstance(data, dict):
        return False, "Данные назначения обязательны"

    expert_id = data.get('expert_id')
    if expert_id is None:
        return False, "Поле expert_id обязательно"

    if not isinstance(expert_id, int) or expert_id <= 0:
        return False, "expert_id должно быть положительным числом"

    return True, None
