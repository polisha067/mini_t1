from flask import jsonify
from werkzeug.exceptions import HTTPException
from .exceptions import APIError

def register_error_handlers(app):
    """Регистрирует обработчики ошибок для Flask приложения"""

    @app.errorhandler(APIError)
    def handle_api_error(error):
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(400)
    def handle_bad_request(error):
        return jsonify({
            'status': 'error',
            'error': {
                'code': 'BAD_REQUEST',
                'message': str(error.description) if hasattr(error, 'description') else 'Неверный запрос'
            }
        }), 400

    @app.errorhandler(401)
    def handle_unauthorized(error):
        return jsonify({
            'status': 'error',
            'error': {
                'code': 'UNAUTHORIZED',
                'message': 'Требуется аутентификация'
            }
        }), 401

    @app.errorhandler(403)
    def handle_forbidden(error):
        return jsonify({
            'status': 'error',
            'error': {
                'code': 'FORBIDDEN',
                'message': 'Доступ запрещён'
            }
        }), 403

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'status': 'error',
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Ресурс не найден'
            }
        }), 404

    @app.errorhandler(409)
    def handle_conflict(error):
        return jsonify({
            'status': 'error',
            'error': {
                'code': 'CONFLICT',
                'message': 'Конфликт данных'
            }
        }), 409

    @app.errorhandler(500)
    def handle_internal_error(error):
        app.logger.error(f'Internal error: {str(error)}')
        return jsonify({
            'status': 'error',
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Внутренняя ошибка сервера'
            }
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled exception: {str(error)}', exc_info=True)

        if isinstance(error, HTTPException):
            return jsonify({
                'status': 'error',
                'error': {
                    'code': error.code,
                    'message': error.description
                }
            }), error.code

        return jsonify({
            'status': 'error',
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Внутренняя ошибка сервера'
            }
        }), 500


def register_jwt_error_handlers(jwt_manager):
    """Обработчики JWT-ошибок"""

    @jwt_manager.expired_token_loader
    def handle_expired_token(jwt_header, jwt_payload):
        return jsonify({
            'status': 'error',
            'error': {
                'code': 'TOKEN_EXPIRED',
                'message': 'Токен истёк'
            }
        }), 401

    @jwt_manager.invalid_token_loader
    def handle_invalid_token(error_string):
        return jsonify({
            'status': 'error',
            'error': {
                'code': 'INVALID_TOKEN',
                'message': 'Недействительный токен'
            }
        }), 401

    @jwt_manager.unauthorized_loader
    def handle_missing_token(error_string):
        return jsonify({
            'status': 'error',
            'error': {
                'code': 'MISSING_TOKEN',
                'message': 'Токен не предоставлен'
            }
        }), 401

    @jwt_manager.revoked_token_loader
    def handle_revoked_token(jwt_header, jwt_payload):
        return jsonify({
            'status': 'error',
            'error': {
                'code': 'TOKEN_REVOKED',
                'message': 'Токен отозван'
            }
        }), 401