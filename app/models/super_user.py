from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


class SuperUser(UserMixin, db.Model):
    """
    Суперпользователь для доступа к Flask-Admin
    Отдельная таблица - НЕ доступна через API
    Создаётся только через CLI команду
    """
    __tablename__ = 'super_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    failed_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)

    #  Настройки безопасности
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30

    def set_password(self, password: str) -> None:
        """Сохраняет хэш пароля"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256:260000')

    def check_password(self, password: str) -> bool:
        """Проверяет пароль с защитой от brute-force"""
        # Проверка блокировки
        if self.locked_until and datetime.utcnow() < self.locked_until:
            return False

        # Проверка пароля
        if check_password_hash(self.password_hash, password):
            # Сброс попыток при успешном входе
            self.failed_attempts = 0
            self.locked_until = None
            self.last_login = datetime.utcnow()
            db.session.commit()
            return True
        else:
            # Увеличение счётчика неудачных попыток
            self.failed_attempts += 1
            if self.failed_attempts >= self.MAX_FAILED_ATTEMPTS:
                self.locked_until = datetime.utcnow() + timedelta(minutes=self.LOCKOUT_DURATION_MINUTES)
            db.session.commit()
            return False

    def is_authenticated(self):
        return self.is_active and (not self.locked_until or datetime.utcnow() >= self.locked_until)

    def __repr__(self):
        return f'<SuperUser {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """Загрузка суперпользователя для Flask-Login"""
    return SuperUser.query.get(int(user_id))