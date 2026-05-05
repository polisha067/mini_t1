from datetime import datetime, UTC, timedelta
import secrets
import hashlib
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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    reset_token_hash = db.Column(db.String(64), nullable=True, index=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)

    contests = db.relationship("Contest", back_populates="organizer", lazy="dynamic")
    grades = db.relationship("Grade", back_populates="expert", lazy="dynamic")
    contest_assignments = db.relationship("ContestExpert", back_populates="expert", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        """Сохраняет хэш пароля"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Проверяет пароль"""
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self) -> str:
        """Генерирует токен сброса пароля, сохраняет хеш в БД, возвращает сырой токен"""
        raw_token = secrets.token_urlsafe(32)
        self.reset_token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        self.reset_token_expires = datetime.now(UTC) + timedelta(hours=1)
        return raw_token

    def verify_reset_token(self, raw_token: str) -> bool:
        """Проверяет токен сброса пароля"""
        if not self.reset_token_hash or not self.reset_token_expires:
            return False
        if datetime.now(UTC) > self.reset_token_expires:
            return False
        expected_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        return secrets.compare_digest(self.reset_token_hash, expected_hash)

    def clear_reset_token(self) -> None:
        """Инвалидирует токен после использования"""
        self.reset_token_hash = None
        self.reset_token_expires = None

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
