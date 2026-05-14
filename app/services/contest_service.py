import os
import logging

from flask import current_app

from app.extensions import db
from app.models.contest import Contest
from app.models.team import Team
from app.models.criterion import Criterion
from app.models.grade import Grade
from app.models.contest_expert import ContestExpert
from app.utils.validators.contest import validate_contest_data
from app.utils.file_upload import save_uploaded_file
from app.utils.errors import (
    ValidationError,
    NotFoundError,
    ForbiddenError,
    BadRequestError,
    ConflictError,
)

logger = logging.getLogger(__name__)


class ContestService:
    """Сервис для управления конкурсами"""

    @staticmethod
    def _get_or_404(contest_id: int) -> Contest:
        contest = db.session.get(Contest, contest_id)
        if not contest:
            raise NotFoundError(f"Конкурс с id={contest_id} не найден")
        return contest

    @staticmethod
    def _check_ownership(contest: Contest, user_id: int) -> None:
        if contest.organizer_id != user_id:
            raise ForbiddenError("Только организатор конкурса может выполнять это действие")

    @staticmethod
    def _delete_local_file(relative_path: str) -> bool:
        if not relative_path:
            return False
        upload_folder = current_app.config.get('UPLOAD_FOLDER', '/app/uploads')
        file_path = os.path.join(upload_folder, relative_path)
        try:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                os.remove(file_path)
                logger.info(f"Deleted old file: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
        except OSError as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False

    @staticmethod
    def create(data: dict, logo_file, user_id: int) -> Contest:
        """Создание нового конкурса"""
        if not data:
            raise BadRequestError("Тело запроса должно быть в формате JSON или multipart/form-data")

        valid, error = validate_contest_data(data)
        if not valid:
            raise ValidationError(error)

        logo_path = None

        if logo_file and logo_file.filename:
            try:
                logo_path = save_uploaded_file(logo_file, folder='logos')
            except ValueError as e:
                raise ValidationError(str(e))
        elif data.get('logo_path'):
            logo_path = data.get('logo_path')

        contest = Contest(
            name=data['name'].strip(),
            description=data.get('description', '').strip() or None,
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            logo_path=logo_path,
            organizer_id=user_id,
            access_key=data.get('access_key')
        )

        try:
            db.session.add(contest)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return contest

    @staticmethod
    def get_list(page: int, per_page: int, organizer_id: int = None):
        """Получение списка конкурсов с пагинацией"""
        per_page = min(per_page, 100)

        query = Contest.query
        if organizer_id:
            query = query.filter_by(organizer_id=organizer_id)

        query = query.order_by(Contest.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_by_id(contest_id: int) -> Contest:
        """Получение конкурса по ID"""
        return ContestService._get_or_404(contest_id)

    def update(self, contest_id: int, data: dict, logo_file, user_id: int) -> Contest:
        """Обновление конкурса"""
        contest = self._get_or_404(contest_id)
        self._check_ownership(contest, user_id)

        if not data:
            raise BadRequestError("Тело запроса должно быть в формате JSON или multipart/form-data")

        valid, error = validate_contest_data(data)
        if not valid:
            raise ValidationError(error)

        if 'name' in data:
            contest.name = data['name'].strip()
        if 'description' in data:
            contest.description = data['description'].strip() or None
        if 'start_date' in data:
            contest.start_date = data['start_date']
        if 'end_date' in data:
            contest.end_date = data['end_date']

        if logo_file and logo_file.filename:
            old_logo_path = contest.logo_path

            try:
                new_logo_path = save_uploaded_file(logo_file, folder='logos')
                contest.logo_path = new_logo_path
                db.session.commit()

                if old_logo_path:
                    self._delete_local_file(old_logo_path)

            except ValueError as e:
                db.session.rollback()
                raise ValidationError(str(e))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Failed to update logo for contest {contest_id}: {e}")
                raise ValidationError("Ошибка при обновлении логотипа")

        elif 'logo_path' in data:
            contest.logo_path = data.get('logo_path')
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

        return contest

    def delete(self, contest_id: int, user_id: int) -> Contest:
        """Удаление конкурса"""
        contest = self._get_or_404(contest_id)
        self._check_ownership(contest, user_id)

        if contest.is_finished:
            raise ForbiddenError("Нельзя удалить завершённый конкурс")

        if contest.logo_path:
            self._delete_local_file(contest.logo_path)

        try:
            db.session.delete(contest)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return contest

    def finalize(self, contest_id: int, user_id: int) -> Contest:
        """Завершение голосования"""
        contest = self._get_or_404(contest_id)
        self._check_ownership(contest, user_id)

        if contest.is_finished:
            raise ConflictError("Голосование уже завершено")

        contest.is_finished = True

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return contest

    @staticmethod
    def get_voting_status(contest_id: int) -> dict:
        """Статус голосования"""
        contest = ContestService._get_or_404(contest_id)

        if contest.is_finished:
            return {
                "contest_id": contest_id,
                "is_finished": True,
                "message": "Голосование завершено"
            }

        teams_count = Team.query.filter_by(contest_id=contest_id).count()
        criteria_count = Criterion.query.filter_by(contest_id=contest_id).count()
        experts_count = ContestExpert.query.filter_by(contest_id=contest_id).count()

        expected_grades = teams_count * criteria_count * experts_count
        actual_grades = Grade.query.join(Team).filter(Team.contest_id == contest_id).count()

        if expected_grades == 0:
            voting_status = "not_started"
            message = "Нет данных для голосования"
        elif actual_grades == 0:
            voting_status = "not_started"
            message = "Никто не выставил оценок"
        elif actual_grades == expected_grades:
            voting_status = "all_votes_cast"
            message = f"Все эксперты выставили оценки ({actual_grades}/{expected_grades})"
        else:
            voting_status = "in_progress"
            missing = expected_grades - actual_grades
            message = f"Голосование в процессе: {actual_grades}/{expected_grades} оценок, не хватает {missing}"

        return {
            "contest_id": contest_id,
            "is_finished": False,
            "voting_status": voting_status,
            "expected_grades": expected_grades,
            "actual_grades": actual_grades,
            "missing_grades": max(0, expected_grades - actual_grades),
            "teams_count": teams_count,
            "criteria_count": criteria_count,
            "experts_count": experts_count,
            "message": message
        }
