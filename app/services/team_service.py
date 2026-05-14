from app.extensions import db
from app.models.contest import Contest
from app.models.team import Team
from app.utils.validators.team import validate_team_data
from app.utils.errors import (
    ValidationError,
    NotFoundError,
    ForbiddenError,
    BadRequestError,
)


class TeamService:
    """Сервис для управления командами"""

    @staticmethod
    def _get_contest_or_404(contest_id: int) -> Contest:
        contest = db.session.get(Contest, contest_id)
        if not contest:
            raise NotFoundError(f"Конкурс с id={contest_id} не найден")
        return contest

    @staticmethod
    def _get_or_404(team_id: int) -> Team:
        team = db.session.get(Team, team_id)
        if not team:
            raise NotFoundError(f"Команда с id={team_id} не найдена")
        return team

    @staticmethod
    def _check_ownership(contest: Contest, user_id: int) -> None:
        if contest.organizer_id != user_id:
            raise ForbiddenError("Только организатор конкурса может выполнять это действие")

    @staticmethod
    def create(contest_id: int, data: dict) -> Team:
        """Создание новой команды"""
        TeamService._get_contest_or_404(contest_id)

        if not data:
            raise BadRequestError("Тело запроса должно быть в формате JSON")

        valid, error = validate_team_data(data)
        if not valid:
            raise ValidationError(error)

        team = Team(
            name=data['name'].strip(),
            description=data.get('description', '').strip() or None,
            contest_id=contest_id
        )

        try:
            db.session.add(team)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return team

    @staticmethod
    def get_list(contest_id: int, page: int, per_page: int):
        """Получение списка команд с пагинацией"""
        TeamService._get_contest_or_404(contest_id)

        per_page = min(per_page, 100)
        query = Team.query.filter_by(contest_id=contest_id)
        query = query.order_by(Team.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_by_id(team_id: int) -> Team:
        """Получение команды по ID"""
        return TeamService._get_or_404(team_id)

    @staticmethod
    def update(team_id: int, data: dict, user_id: int) -> Team:
        """Обновление команды"""
        team = TeamService._get_or_404(team_id)
        contest = TeamService._get_contest_or_404(team.contest_id)
        TeamService._check_ownership(contest, user_id)

        if not data:
            raise BadRequestError("Тело запроса должно быть в формате JSON")

        valid, error = validate_team_data(data)
        if not valid:
            raise ValidationError(error)

        if 'name' in data:
            team.name = data['name'].strip()
        if 'description' in data:
            team.description = data['description'].strip() or None

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return team

    @staticmethod
    def delete(team_id: int, user_id: int) -> Team:
        """Удаление команды"""
        team = TeamService._get_or_404(team_id)
        contest = TeamService._get_contest_or_404(team.contest_id)
        TeamService._check_ownership(contest, user_id)

        try:
            db.session.delete(team)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return team
