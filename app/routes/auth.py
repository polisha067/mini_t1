from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from flasgger import swag_from

from app.services.auth_service import AuthService
from app.extensions import mail
from flask_mail import Message
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
@swag_from('../specs/swagger/register.yml')
def register():
    """Регистрация нового пользователя"""
    data = request.get_json(silent=True)
    user = AuthService.register(data)

    return jsonify({
        "status": "success",
        "message": "Пользователь успешно зарегистрирован",
        "user": user.to_dict(),
        "redirect_url": AuthService.get_redirect_url_for_role(user.role)
    }), 201


@auth_bp.route('/login', methods=['POST'])
@swag_from('../specs/swagger/login.yml')
def login():
    """Аутентификация пользователя и выдача JWT токена"""
    data = request.get_json(silent=True)
    user, access_token, refresh_token = AuthService.login(data)

    return jsonify({
        "status": "success",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict(),
        "redirect_url": AuthService.get_redirect_url_for_role(user.role)
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
@swag_from('../specs/swagger/me.yml')
def me():
    """Защищённый эндпоинт: данные текущего пользователя"""
    user_id = int(get_jwt_identity())
    user = AuthService.get_user_by_id(user_id)

    return jsonify({
        "status": "success",
        "user": user.to_dict()
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@swag_from('../specs/swagger/refresh.yml')
def refresh():
    """Обновление access токена с помощью refresh токена"""
    identity = get_jwt_identity()
    user, new_access_token = AuthService.refresh_access_token(identity)

    return jsonify({
        "status": "success",
        "access_token": new_access_token
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Выход из системы (на клиенте нужно удалить оба токена)"""
    return jsonify({
        "status": "success",
        "message": "Выход выполнен успешно"
    }), 200


@auth_bp.route('/forgot-password', methods=['POST'])
@swag_from('../specs/swagger/forgot_password.yml')
def forgot_password():
    """Запрос токена для сброса пароля"""
    data = request.get_json(silent=True)
    user_found, raw_token = AuthService.forgot_password(data)

    if user_found:
        email = data.get('email', '')
        # В Production ссылаемся на IP сервера или домен. Для локальной разработки можно оставить localhost через env.
        base_url = current_app.config.get('CORS_ORIGINS', ['http://localhost:4200'])[0]
        if base_url == '*':
            base_url = 'http://103.76.54.43'
        
        reset_link = f"{base_url}/reset-password?token={raw_token}"
        
        try:
            msg = Message(
                subject="Сброс пароля (Hackathon System)",
                recipients=[email],
                body=f"Здравствуйте!\n\nДля сброса пароля перейдите по следующей ссылке:\n{reset_link}\n\nЕсли вы не запрашивали сброс пароля, проигнорируйте это письмо."
            )
            mail.send(msg)
            current_app.logger.info(f"Письмо для сброса пароля успешно отправлено на {email}")
        except Exception as e:
            current_app.logger.error(f"Ошибка при отправке письма на {email}: {str(e)}")
        response_data = {
            "status": "success",
            "message": "Если email зарегистрирован, токен сброса пароля будет отправлен",
            "expires_in_minutes": 60
        }
        # В локальной разработке возвращаем токен прямо в ответе для удобства тестирования без почты
        if current_app.config.get('DEBUG'):
            response_data['reset_token'] = raw_token
            
        return jsonify(response_data), 200

    return jsonify({
        "status": "success",
        "message": "Если email зарегистрирован, токен сброса пароля будет отправлен"
    }), 200


@auth_bp.route('/reset-password', methods=['POST'])
@swag_from('../specs/swagger/reset_password.yml')
def reset_password():
    """Сброс пароля по токену"""
    data = request.get_json(silent=True)
    AuthService.reset_password(data)

    return jsonify({
        "status": "success",
        "message": "Пароль успешно изменён"
    }), 200