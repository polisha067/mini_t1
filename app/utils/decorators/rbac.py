from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from app.utils.errors import ForbiddenError, UnauthorizedError


def role_required(required_role: str):
    """Декоратор для защиты маршрутов на основе одной роли"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):

            verify_jwt_in_request()
            
            claims = get_jwt()
            user_role = claims.get('role')
            
            if not user_role:
                raise ForbiddenError("Роль пользователя не определена")
            
            if user_role != required_role:
                raise ForbiddenError(f"Требуется роль '{required_role}'")
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """Декоратор для защиты маршрутов, доступных только администратору"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        
        claims = get_jwt()
        user_role = claims.get('role')
        
        if not user_role:
            raise ForbiddenError("Роль пользователя не определена")
        
        if user_role != 'admin':
            raise ForbiddenError("Требуется роль 'admin'")
        
        return fn(*args, **kwargs)
    return wrapper
