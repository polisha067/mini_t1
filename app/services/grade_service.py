from app.extensions import db
from app.models.grade import Grade
from app.models.team import Team
from app.models.criterion import Criterion
from app.models.contest import Contest
from app.models.contest_expert import ContestExpert
from app.utils.validators.grade import validate_grade_data
from app.utils.errors import (
    ValidationError,
    NotFoundError,
    ForbiddenError,
    BadRequestError,
    ConflictError,
)


class GradeService:
    """Сервис для управления оценками"""

    @staticmethod
    def _get_or_404(grade_id: int) -> Grade:
        grade = db.session.get(Grade, grade_id)
        if not grade:
            raise NotFoundError(f"Оценка с id={grade_id} не найдена")
        return grade

    @staticmethod
    def _get_team_or_404(team_id: int) -> Team:
        team = db.session.get(Team, team_id)
        if not team:
            raise NotFoundError(f"Команда с id={team_id} не найдена")
        return team

    @staticmethod
    def _get_criterion_or_404(criterion_id: int) -> Criterion:
        criterion = db.session.get(Criterion, criterion_id)
        if not criterion:
            raise NotFoundError(f"Критерий с id={criterion_id} не найден")
        return criterion

    @staticmethod
    def _check_expert_ownership(grade: Grade, user_id: int) -> None:
        if grade.expert_id != user_id:
            raise ForbiddenError("Эксперт может редактировать только свои оценки")

    @staticmethod
    def create(data: dict, expert_id: int) -> Grade:
        """Выставление оценки"""
        if not data:
            raise BadRequestError("Тело запроса должно быть в формате JSON")

        team_id = data.get('team_id')
        criterion_id = data.get('criterion_id')

        if not team_id or not criterion_id or 'value' not in data:
            raise ValidationError("Поля team_id, criterion_id и value обязательны")

        team = GradeService._get_team_or_404(team_id)
        criterion = GradeService._get_criterion_or_404(criterion_id)

        if criterion.contest_id != team.contest_id:
            raise ValidationError("Критерий не принадлежит данной команде")

        contest = db.session.get(Contest, team.contest_id)
        if contest and contest.is_finished:
            raise ForbiddenError("Голосование по этому конкурсу завершено")

        assignment = ContestExpert.query.filter_by(
            contest_id=team.contest_id,
            user_id=expert_id
        ).first()
        if not assignment:
            raise ForbiddenError("Вы не назначены на этот конкурс")

        existing = Grade.query.filter_by(
            expert_id=expert_id,
            team_id=team_id,
            criterion_id=criterion_id
        ).first()
        if existing:
            raise ConflictError("Вы уже выставили оценку этой команде по данному критерию")

        valid, error = validate_grade_data(data, criterion.max_score)
        if not valid:
            raise ValidationError(error)

        grade = Grade(
            expert_id=expert_id,
            team_id=team_id,
            criterion_id=criterion_id,
            value=data['value'],
            comment=data.get('comment', '').strip() or None,
        )

        try:
            db.session.add(grade)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return grade

    @staticmethod
    def get_list_by_team(team_id: int) -> list:
        """Получение всех оценок команды"""
        GradeService._get_team_or_404(team_id)

        query = Grade.query.filter_by(team_id=team_id)
        query = query.order_by(Grade.id.asc())
        return query.all()

    @staticmethod
    def get_list_by_expert(expert_id: int, current_user_id: int) -> list:
        """Получение всех оценок эксперта"""
        if current_user_id != expert_id:
            raise ForbiddenError("Вы можете просматривать только свои оценки")

        query = Grade.query.filter_by(expert_id=expert_id)
        query = query.order_by(Grade.created_at.desc())
        return query.all()

    @staticmethod
    def update(grade_id: int, data: dict, user_id: int) -> Grade:
        """Редактирование оценки"""
        grade = GradeService._get_or_404(grade_id)
        GradeService._check_expert_ownership(grade, user_id)

        team = GradeService._get_team_or_404(grade.team_id)
        contest = db.session.get(Contest, team.contest_id)
        if contest and contest.is_finished:
            raise ForbiddenError("Голосование по этому конкурсу завершено")

        if not data:
            raise BadRequestError("Тело запроса должно быть в формате JSON")

        if 'value' in data:
            criterion = GradeService._get_criterion_or_404(grade.criterion_id)
            valid, error = validate_grade_data({'value': data['value']}, criterion.max_score)
            if not valid:
                raise ValidationError(error)
            grade.value = data['value']

        if 'comment' in data:
            comment = data['comment']
            if comment and len(comment) > 3000:
                raise ValidationError("Комментарий слишком длинный (максимум 3000 символов)")
            grade.comment = comment.strip() or None

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return grade

    @staticmethod
    def delete(grade_id: int, user_id: int) -> Grade:
        """Удаление оценки"""
        grade = GradeService._get_or_404(grade_id)
        GradeService._check_expert_ownership(grade, user_id)

        team = GradeService._get_team_or_404(grade.team_id)
        contest = db.session.get(Contest, team.contest_id)
        if contest and contest.is_finished:
            raise ForbiddenError("Голосование по этому конкурсу завершено")

        try:
            db.session.delete(grade)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return grade
