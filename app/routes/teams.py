from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

from app.extensions import db
from app.models.team import Team
from app.utils.decorators.rbac import role_required
from app.utils.errors import (
    ValidationError,
    NotFoundError,
    ForbiddenError,
    BadRequestError,
)

contests_bp = Blueprint('teams', __name__, url_prefix='/teams')

def _get_current_user_id() -> int:
    """Получить ID текущего пользователя из JWT токена"""
    return int(get_jwt_identity())


def _get_team_or_404(team_id: int) -> Team:
    """Получить команду или выбросить NotFoundError"""
    team = db.session.get(Team, team_id)
    if not team:
        raise NotFoundError(f"Команда с id={team_id} не найдена")
    return team