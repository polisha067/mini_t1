from flask_jwt_extended import JWTManager
from app.extensions import db
from app.models.user import User


def init_jwt(jwt: JWTManager):
    """Инициализация JWT, добавляет роль пользователя в JWT токен"""
    
    @jwt.additional_claims_loader
    def add_role_to_token(identity):
        user = db.session.get(User, identity)
        if user:
            return {'role': user.role}
        return {'role': 'user'}
    
    @jwt.user_identity_loader
    def user_identity_lookup(identity):
        if hasattr(identity, 'id'):
            return str(identity.id)
        return str(identity)