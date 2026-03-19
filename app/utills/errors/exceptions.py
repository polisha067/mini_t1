class APIError(Exception):
    """Базовый класс для API ошибок"""
    status_code = 500
    error_code = 'INTERNAL_ERROR'

    def __init__(self, message: str, status_code: int = None, error_code: str = None):
        super().__init__(message)
        self.message = message
        if status_code:
            self.status_code = status_code
        if error_code:
            self.error_code = error_code

    def to_dict(self):
        return {
            'status': 'error',
            'error': {
                'code': self.error_code,
                'message': self.message
            }
        }


class BadRequestError(APIError):
    """400 Bad Request - неверные данные запроса"""
    status_code = 400
    error_code = 'BAD_REQUEST'


class UnauthorizedError(APIError):
    """401 Unauthorized - требуется аутентификация"""
    status_code = 401
    error_code = 'UNAUTHORIZED'


class ForbiddenError(APIError):
    """403 Forbidden - доступ запрещён"""
    status_code = 403
    error_code = 'FORBIDDEN'


class NotFoundError(APIError):
    """404 Not Found - ресурс не найден"""
    status_code = 404
    error_code = 'NOT_FOUND'


class ConflictError(APIError):
    """409 Conflict - конфликт данных"""
    status_code = 409
    error_code = 'CONFLICT'


class ValidationError(APIError):
    """422 Unprocessable Entity - ошибка валидации"""
    status_code = 422
    error_code = 'VALIDATION_ERROR'