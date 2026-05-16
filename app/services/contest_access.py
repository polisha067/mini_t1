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
    - без авторизации — публичное чтение (таблица, рейтинг);
    - организатор — только свой конкурс;
    - эксперт — только если присоединился по ключу (ContestExpert).
    """
    if viewer_user_id is None:
        return

    user = db.session.get(User, viewer_user_id)
    if not user:
        return

    contest = db.session.get(Contest, contest_id)
    if not contest:
        return

    if user.role == "organizer":
        if contest.organizer_id != viewer_user_id:
            raise ForbiddenError("Вы не организатор этого конкурса")
        return

    if user.role == "expert":
        if not ContestExpert.query.filter_by(
            contest_id=contest_id, user_id=viewer_user_id
        ).first():
            raise ForbiddenError(
                "Сначала присоединитесь к конкурсу по ключу в личном кабинете эксперта."
            )
        return

    raise ForbiddenError("Недостаточно прав для просмотра данных конкурса")
