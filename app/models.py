from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    """Пользователь системы"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    contests = db.relationship("Contest", back_populates="organizer", lazy="dynamic")
    grades = db.relationship("Grade", back_populates="expert", lazy="dynamic")
    contest_assignments = db.relationship("ContestExpert", back_populates="expert", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        """Сохраняет хэш пароля"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Проверяет пароль"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Сериализация для API"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<User {self.username}>'


class Contest(db.Model):
    """Конкурс (хакатон)"""
    __tablename__ = "contests"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    organizer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    organizer = db.relationship("User", back_populates="contests")
    teams = db.relationship("Team", back_populates="contest", cascade="all, delete-orphan")
    criteria = db.relationship("Criterion", back_populates="contest", cascade="all, delete-orphan")
    assigned_experts = db.relationship("ContestExpert", back_populates="contest", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'organizer_id': self.organizer_id
        }

    def __repr__(self):
        return f'<Contest {self.name}>'


class Team(db.Model):
    """Команда-участник конкурса"""
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    contest_id = db.Column(db.Integer, db.ForeignKey("contests.id"), nullable=False, index=True)

    contest = db.relationship("Contest", back_populates="teams")
    grades = db.relationship("Grade", back_populates="team", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contest_id': self.contest_id
        }

    def __repr__(self):
        return f'<Team {self.name}>'


class Criterion(db.Model):
    """Критерий оценивания внутри конкурса"""
    __tablename__ = "criteria"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    max_score = db.Column(db.Integer, nullable=False, default=10)

    contest_id = db.Column(db.Integer, db.ForeignKey("contests.id"), nullable=False, index=True)

    contest = db.relationship("Contest", back_populates="criteria")
    grades = db.relationship("Grade", back_populates="criterion", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'max_score': self.max_score,
            'contest_id': self.contest_id
        }

    def __repr__(self):
        return f'<Criterion {self.name}>'


class Grade(db.Model):
    """Оценка эксперта за конкретную команду по конкретному критерию"""
    __tablename__ = "grades"

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    expert_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False, index=True)
    criterion_id = db.Column(db.Integer, db.ForeignKey("criteria.id"), nullable=False, index=True)

    expert = db.relationship("User", back_populates="grades")
    team = db.relationship("Team", back_populates="grades")
    criterion = db.relationship("Criterion", back_populates="grades")

    __table_args__ = (
        db.UniqueConstraint("expert_id", "team_id", "criterion_id", name="uix_grade_expert_team_criterion"),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'value': self.value,
            'expert_id': self.expert_id,
            'team_id': self.team_id,
            'criterion_id': self.criterion_id,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Grade {self.value} (Expert {self.expert_id} -> Team {self.team_id})>'


class ContestExpert(db.Model):
    """Таблица связи для назначения экспертов на конкретные конкурсы"""
    __tablename__ = 'contest_experts'

    id = db.Column(db.Integer, primary_key=True)
    contest_id = db.Column(db.Integer, db.ForeignKey('contests.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    contest = db.relationship('Contest', back_populates='assigned_experts')
    expert = db.relationship('User', back_populates='contest_assignments')

    __table_args__ = (
        db.UniqueConstraint('contest_id', 'user_id', name='uix_contest_expert'),
    )

    def __repr__(self):
        return f'<ContestExpert User {self.user_id} -> Contest {self.contest_id}>'
