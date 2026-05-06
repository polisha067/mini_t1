import secrets
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from app.extensions import db
from app.models import User, Contest, ContestExpert
from app.utils.errors import BadRequestError, NotFoundError, ForbiddenError, ValidationError

expert_bp = Blueprint('experts', __name__, url_prefix='/experts')

def _get_current_user_id() -> int:
    return int(get_jwt_identity())

def _get_contest_or_404(contest_id: int) -> Contest:
    contest = db.session.get(Contest, contest_id)
    if not contest:
        raise NotFoundError(f"Конкурс с id={contest_id} не найден")
    return contest

def _check_organizer_ownership(contest: Contest, user_id: int) -> None:
    if contest.organizer_id != user_id:
        raise ForbiddenError("Только организатор может управлять этим конкурсом")

@expert_bp.route('/contests/<int:contest_id>/access-key/generate', methods=['POST'])
@jwt_required()
def generate_access_key(contest_id: int):
    contest = _get_contest_or_404(contest_id)
    user_id = _get_current_user_id()
    _check_organizer_ownership(contest, user_id)

    new_key = secrets.token_urlsafe(24)
    contest.access_key = new_key
    try:
        db.session.add(contest)
        db.session.commit()
        db.session.expire_all()
        return jsonify({"status": "success", "access_key": new_key}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.session.remove()

@expert_bp.route('/contests/<int:contest_id>/join', methods=['POST'])
@jwt_required()
def join_contest_by_key(contest_id: int):
    data = request.get_json()
    access_key = data.get('access_key')
    user_id = _get_current_user_id()
    
    contest = _get_contest_or_404(contest_id)
    if contest.access_key != access_key:
        raise ValidationError("Неверный ключ доступа")

    existing = ContestExpert.query.filter_by(contest_id=contest_id, user_id=user_id).first()
    if existing:
        return jsonify({"status": "success", "message": "Вы уже присоединились к этому конкурсу"}), 200

    assignment = ContestExpert(contest_id=contest_id, user_id=user_id)
    try:
        db.session.add(assignment)
        db.session.commit()
        db.session.expire_all()
        return jsonify({"status": "success", "message": "Вы успешно присоединились к конкурсу"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.session.remove()

@expert_bp.route('/me/contests', methods=['GET'])
@jwt_required()
def get_expert_contests():
    expert_id = _get_current_user_id()
    try:
        assignments = ContestExpert.query.filter_by(user_id=expert_id).all()
        contest_ids = [a.contest_id for a in assignments]
        
        if not contest_ids:
            return jsonify({"status": "success", "contests": []}), 200
            
        contests = Contest.query.filter(Contest.id.in_(contest_ids)).all()
        
        return jsonify({
            "status": "success",
            "contests": [c.to_dict() for c in contests]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.session.remove()
