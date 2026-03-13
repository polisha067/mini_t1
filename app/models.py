from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(db.Model):
    """
    Пользователь системы.

    Может иметь одну из двух ролей:
    - 'organizer' — создаёт конкурсы, команды и критерии
    - 'expert' — выставляет оценки командам по критериям
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'organizer' или 'expert'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связь с конкурсами, которые создал организатор
    contests = db.relationship("Contest", back_populates="organizer", lazy="dynamic")

    # Связь с оценками, которые поставил эксперт
    scores = db.relationship("Score", back_populates="expert", lazy="dynamic")

    def set_password(self, password: str) -> None:
        """Сохраняет хэш пароля"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Проверяет, совпадает ли введённый пароль с хранимым хэшем"""
        return check_password_hash(self.password_hash, password)


class Contest(db.Model):
    """
    хакатон / хакатон
    Организатор создаёт конкурс, в рамках которого есть команды и критерии оценивания
    """

    __tablename__ = "contests"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)

    organizer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    organizer = db.relationship("User", back_populates="contests")
    teams = db.relationship("Team", back_populates="contest", cascade="all, delete-orphan")
    criteria = db.relationship("Criterion", back_populates="contest", cascade="all, delete-orphan")


class Team(db.Model):
    """
    Команда конкурса
    Каждая команда участвует в одном конкурсе
    """

    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    contest_id = db.Column(db.Integer, db.ForeignKey("contests.id"), nullable=False)

    contest = db.relationship("Contest", back_populates="teams")
    scores = db.relationship("Score", back_populates="team", cascade="all, delete-orphan")


class Criterion(db.Model):
    """
    Критерий оценивания
    """

    __tablename__ = "criteria"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Максимальный балл по этому критерию 
    max_score = db.Column(db.Integer, nullable=False, default=10)

    contest_id = db.Column(db.Integer, db.ForeignKey("contests.id"), nullable=False)

    contest = db.relationship("Contest", back_populates="criteria")
    scores = db.relationship("Score", back_populates="criterion", cascade="all, delete-orphan")


class Score(db.Model):
    """
    Оценка эксперта за конкретную команду по конкретному критерию

    один эксперт может один раз оценить одну команду по одному критерию
    если он меняет оценку - запись обновляется
    """

    __tablename__ = "scores"

    id = db.Column(db.Integer, primary_key=True)

    value = db.Column(db.Integer, nullable=False)  # фактический балл (0–max_score)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    expert_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    criterion_id = db.Column(db.Integer, db.ForeignKey("criteria.id"), nullable=False)

    expert = db.relationship("User", back_populates="scores")
    team = db.relationship("Team", back_populates="scores")
    criterion = db.relationship("Criterion", back_populates="scores")

    # Уникальность, один эксперт одна команда один критерий
    __table_args__ = (
        db.UniqueConstraint(
            "expert_id", "team_id", "criterion_id", name="uix_score_expert_team_criterion"
        ),
    )

