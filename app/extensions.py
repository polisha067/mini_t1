from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
login_manager = LoginManager()

# Настройка Flask-Login для защиты админки
login_manager.login_view = 'admin.login'
login_manager.login_message = 'Требуется авторизация администратора'
login_manager.login_message_category = 'warning'
login_manager.session_protection = 'strong'