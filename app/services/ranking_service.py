from sqlalchemy import func

from app.extensions import db
from app.models.team import Team
from app.models.grade import Grade
from app.models.contest import Contest
from app.models.criterion import Criterion
from app.utils.errors import NotFoundError


class RankingService:
    """Сервис для расчёта рейтинга команд"""

    @staticmethod
    def _get_contest_or_404(contest_id: int) -> Contest:
        contest = db.session.get(Contest, contest_id)
        if not contest:
            raise NotFoundError(f"Конкурс с id={contest_id} не найден")
        return contest

    @staticmethod
    def get_ranking(contest_id: int, page: int, per_page: int, sort_order: str = 'desc') -> dict:
        """Получение итогового рейтинга команд с пагинацией"""
        RankingService._get_contest_or_404(contest_id)

        per_page = min(per_page, 100)

        has_grades = db.session.query(Grade.id).join(
            Team, Grade.team_id == Team.id
        ).filter(Team.contest_id == contest_id).first() is not None

        if not has_grades:
            teams_query = Team.query.filter_by(contest_id=contest_id).order_by(Team.name.asc())
            pagination = teams_query.paginate(page=page, per_page=per_page, error_out=False)

            ranking = []
            start_rank = (page - 1) * per_page + 1
            for idx, team in enumerate(pagination.items, start=start_rank):
                ranking.append({
                    "rank": idx,
                    "team_id": team.id,
                    "team_name": team.name,
                    "total_score": 0.0,
                    "grades_count": 0
                })

            return {
                "contest_id": contest_id,
                "ranking": ranking,
                "pagination": {
                    "page": pagination.page,
                    "per_page": pagination.per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "has_next": pagination.has_next,
                    "has_prev": pagination.has_prev,
                }
            }

        # Подзапрос: среднее по каждому (команда, критерий)
        subquery = (
            db.session.query(
                Team.id.label('team_id'),
                Team.name.label('team_name'),
                func.avg(Grade.value).label('avg_score'),
            )
            .outerjoin(Grade, Grade.team_id == Team.id)
            .filter(Team.contest_id == contest_id)
            .group_by(Team.id, Team.name, Grade.criterion_id)
            .subquery()
        )

        # Внешний запрос: суммируем средние по всем критериям
        query = db.session.query(
            subquery.c.team_id,
            subquery.c.team_name,
            func.coalesce(func.sum(subquery.c.avg_score), 0).label('total_score'),
        ).group_by(
            subquery.c.team_id,
            subquery.c.team_name
        )

        if sort_order == 'desc':
            query = query.order_by(func.sum(subquery.c.avg_score).desc())
        else:
            query = query.order_by(func.sum(subquery.c.avg_score).asc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        grades_count_map = dict(
            db.session.query(Grade.team_id, func.count(Grade.id))
            .join(Team, Grade.team_id == Team.id)
            .filter(Team.contest_id == contest_id)
            .group_by(Grade.team_id)
            .all()
        )

        ranking = []
        start_rank = (page - 1) * per_page + 1

        for idx, row in enumerate(pagination.items, start=start_rank):
            ranking.append({
                "rank": idx,
                "team_id": row.team_id,
                "team_name": row.team_name,
                "total_score": round(float(row.total_score), 2),
                "grades_count": grades_count_map.get(row.team_id, 0)
            })

        return {
            "contest_id": contest_id,
            "ranking": ranking,
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            }
        }

    @staticmethod
    def get_team_scores(contest_id: int, team_id: int) -> dict:
        """Средние оценки команды по каждому критерию (как в итоговом рейтинге)."""
        RankingService._get_contest_or_404(contest_id)

        team = db.session.get(Team, team_id)
        if not team or team.contest_id != contest_id:
            raise NotFoundError(f"Команда с id={team_id} не найдена в конкурсе {contest_id}")

        criteria = (
            Criterion.query.filter_by(contest_id=contest_id)
            .order_by(Criterion.id.asc())
            .all()
        )

        criteria_scores = []
        total_score = 0.0

        for criterion in criteria:
            row = (
                db.session.query(
                    func.avg(Grade.value).label("avg_score"),
                    func.count(Grade.id).label("grades_count"),
                )
                .filter(
                    Grade.team_id == team_id,
                    Grade.criterion_id == criterion.id,
                )
                .first()
            )
            avg = row.avg_score if row else None
            count = int(row.grades_count or 0) if row else 0
            avg_val = round(float(avg), 2) if avg is not None else None
            if avg_val is not None:
                total_score += avg_val

            criteria_scores.append({
                "criterion_id": criterion.id,
                "criterion_name": criterion.name,
                "criterion_description": criterion.description,
                "max_score": criterion.max_score,
                "average_score": avg_val,
                "grades_count": count,
            })

        return {
            "contest_id": contest_id,
            "team_id": team.id,
            "team_name": team.name,
            "total_score": round(total_score, 2),
            "criteria_scores": criteria_scores,
        }
