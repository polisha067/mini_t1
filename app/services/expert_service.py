import secrets

from app.extensions import db
from app.models.user import User
from app.models.contest import Contest
from app.models.contest_expert import ContestExpert
from app.utils.errors import NotFoundError, ForbiddenError, ValidationError, BadRequestError


class ExpertService:
    """Сервис для управления экспертами и их назначениями"""

    @staticmethod
    def _get_contest_or_404(contest_id: int) -> Contest:
        contest = db.session.get(Contest, contest_id)
        if not contest:
            raise NotFoundError(f"Конкурс с id={contest_id} не найден")
        return contest

    @staticmethod
    def _check_ownership(contest: Contest, user_id: int) -> None:
        if contest.organizer_id != user_id:
            raise ForbiddenError("Только организатор может управлять этим конкурсом")

    @staticmethod
    def generate_access_key(contest_id: int, user_id: int) -> str:
        """Генерация ключа доступа для конкурса"""
        contest = ExpertService._get_contest_or_404(contest_id)
        ExpertService._check_ownership(contest, user_id)

        new_key = secrets.token_urlsafe(24)
        contest.access_key = new_key

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return new_key

    @staticmethod
    def join_contest(contest_id: int, data: dict, user_id: int) -> tuple[bool, str]:
        """Присоединение эксперта к конкурсу. Возвращает (is_new, message)"""
        if not data:
            raise BadRequestError("Тело запроса должно быть в формате JSON")

        access_key = data.get('access_key')
        if not access_key:
            raise ValidationError("Поле access_key обязательно")

        contest = ExpertService._get_contest_or_404(contest_id)

        # Организаторы не могут быть экспертами в этой системе
        user = db.session.get(User, user_id)
        if user and user.role == 'organizer':
            raise ForbiddenError("Организатор не может присоединиться к конкурсу как эксперт")

        if contest.access_key != access_key:
            raise ValidationError("Неверный ключ доступа")

        existing = ContestExpert.query.filter_by(contest_id=contest_id, user_id=user_id).first()
        if existing:
            return False, "Вы уже присоединились к этому конкурсу"

        assignment = ContestExpert(contest_id=contest_id, user_id=user_id)

        try:
            db.session.add(assignment)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return True, "Вы успешно присоединились к конкурсу"

    @staticmethod
    def get_expert_contests(expert_id: int) -> list:
        """Получение списка конкурсов эксперта"""
        assignments = ContestExpert.query.filter_by(user_id=expert_id).all()
        contest_ids = [a.contest_id for a in assignments]

        if not contest_ids:
            return []

        contests = Contest.query.filter(Contest.id.in_(contest_ids)).all()
        return contests

    @staticmethod
    def get_contest_experts(contest_id: int) -> list:
        """Получение списка экспертов конкурса"""
        ExpertService._get_contest_or_404(contest_id)
        
        assignments = ContestExpert.query.filter_by(contest_id=contest_id).all()
        user_ids = [a.user_id for a in assignments]
        
        if not user_ids:
            return []
            
        experts = User.query.filter(User.id.in_(user_ids)).all()
        return experts
