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
