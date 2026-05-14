from app.extensions import db
from app.models.contest import Contest
from app.models.criterion import Criterion
from app.models.grade import Grade
from app.utils.validators.criterion import validate_criterion_data
from app.utils.errors import (
    ValidationError,
    NotFoundError,
    ForbiddenError,
    BadRequestError,
)


class CriterionService:
    """Сервис для управления критериями оценивания"""

    @staticmethod
    def _get_contest_or_404(contest_id: int) -> Contest:
        contest = db.session.get(Contest, contest_id)
        if not contest:
            raise NotFoundError(f"Конкурс с id={contest_id} не найден")
        return contest

    @staticmethod
    def _get_or_404(criterion_id: int) -> Criterion:
        criterion = db.session.get(Criterion, criterion_id)
        if not criterion:
            raise NotFoundError(f"Критерий с id={criterion_id} не найден")
        return criterion

    @staticmethod
    def _check_ownership(contest: Contest, user_id: int) -> None:
        if contest.organizer_id != user_id:
            raise ForbiddenError("Только организатор конкурса может выполнять это действие")

    @staticmethod
    def create(contest_id: int, data: dict, user_id: int) -> Criterion:
        """Создание нового критерия"""
        contest = CriterionService._get_contest_or_404(contest_id)
        CriterionService._check_ownership(contest, user_id)

        if not data:
            raise BadRequestError("Тело запроса должно быть в формате JSON")

        valid, error = validate_criterion_data(data)
        if not valid:
            raise ValidationError(error)

        criterion = Criterion(
            name=data['name'].strip(),
            description=data.get('description', '').strip() or None,
            max_score=data.get('max_score', 10),
            contest_id=contest_id,
        )

        try:
            db.session.add(criterion)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return criterion

    @staticmethod
    def get_list(contest_id: int) -> list:
        """Получение списка критериев конкурса"""
        CriterionService._get_contest_or_404(contest_id)

        query = Criterion.query.filter_by(contest_id=contest_id)
        query = query.order_by(Criterion.id.asc())
        return query.all()

    @staticmethod
    def get_by_id(criterion_id: int) -> Criterion:
        """Получение критерия по ID"""
        return CriterionService._get_or_404(criterion_id)

    @staticmethod
    def update(criterion_id: int, data: dict, user_id: int) -> Criterion:
        """Обновление критерия"""
        criterion = CriterionService._get_or_404(criterion_id)
        contest = CriterionService._get_contest_or_404(criterion.contest_id)
        CriterionService._check_ownership(contest, user_id)

        has_grades = Grade.query.filter_by(criterion_id=criterion_id).first()
        if has_grades:
            raise ForbiddenError("Нельзя изменить критерий - уже выставлены оценки")

        if not data:
            raise BadRequestError("Тело запроса должно быть в формате JSON")

        valid, error = validate_criterion_data(data)
        if not valid:
            raise ValidationError(error)

        if 'name' in data:
            criterion.name = data['name'].strip()
        if 'description' in data:
            criterion.description = data['description'].strip() or None
        if 'max_score' in data:
            criterion.max_score = data['max_score']

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return criterion

    @staticmethod
    def delete(criterion_id: int, user_id: int) -> Criterion:
        """Удаление критерия"""
        criterion = CriterionService._get_or_404(criterion_id)
        contest = CriterionService._get_contest_or_404(criterion.contest_id)
        CriterionService._check_ownership(contest, user_id)

        try:
            db.session.delete(criterion)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return criterion
