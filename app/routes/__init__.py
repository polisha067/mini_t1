from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from app.extensions import db
from app.models.user import User
from app.routes.auth import auth_bp
from app.routes.contests import contests_bp
from app.routes.teams import teams_bp, teams_detail_bp
from app.routes.criteria import criteria_bp, criteria_detail_bp
from app.routes.grade import grades_bp, grades_by_team_bp, grades_by_expert_bp
from app.routes.ranking import ranking_bp

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/status', methods=['GET'])
@swag_from('../specs/swagger/status.yml')
def status():
    """Статус сервера"""
    return jsonify({
        "server": "running",
        "version": "0.1.0"
    }), 200


@bp.route('/home', methods=['GET'])
@jwt_required(optional=True)
@swag_from('../specs/swagger/home.yml')
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
bp.register_blueprint(contests_bp)
bp.register_blueprint(teams_bp)
bp.register_blueprint(teams_detail_bp)
bp.register_blueprint(criteria_bp)
bp.register_blueprint(criteria_detail_bp)
bp.register_blueprint(grades_bp)
bp.register_blueprint(grades_by_team_bp)
bp.register_blueprint(grades_by_expert_bp)
bp.register_blueprint(ranking_bp)