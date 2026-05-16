from typing import Optional

from app.extensions import db
from app.models.user import User
from app.models.contest import Contest
from app.models.contest_expert import ContestExpert
from app.utils.errors import ForbiddenError


def ensure_can_read_contest_teams_and_criteria(
    contest_id: int, viewer_user_id: Optional[int]
) -> None:
    """
    Список команд и критериев конкурса:
    Публичное чтение доступно всем (анонимам, экспертам, организаторам)
    Защита на выставление оценок находится в grade_service
    """
    return
