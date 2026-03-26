from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.routes.auth import auth_bp

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/status', methods=['GET'])
def status():
    """Статус сервера"""
    return jsonify({
        "server": "running",
        "version": "0.1.0"
    }), 200


@bp.route('/home', methods=['GET'])
@jwt_required(optional=True)
def home():
    """Главная страница - информация для отображения home page"""
    user_id = get_jwt_identity()
    user = None
    user_data = None
    
    if user_id:
        user = db.session.get(User, int(user_id))
        if user:
            user_data = user.to_dict()
    
    return jsonify({
        "status": "success",
        "page": "home",
        "user": user_data,
        "is_authenticated": user is not None
    }), 200

bp.register_blueprint(auth_bp)
