from typing import Tuple, Optional

def validate_join_key_data(data: dict) -> Tuple[bool, Optional[str]]:
    """Проверка данных для вступления эксперта по ключу доступа"""
    if not data or not isinstance(data, dict):
        return False, "Тело запроса должно быть в формате JSON"

    access_key = data.get('access_key')
    if access_key is None or not isinstance(access_key, str):
        return False, "Поле 'access_key' обязательно и должно быть строкой"

    access_key = access_key.strip()
    if not access_key:
        return False, "Ключ доступа не может быть пустым"

    return True, None