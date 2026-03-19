import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from flask import Flask
from flask_cors import CORS
from app.config import config
from app.extensions import db, migrate, jwt
from app import routes
from app.utils.errors import register_error_handlers


def create_app(config_name=None):
    """Factory function для создания Flask приложения"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # CORS для Angular
    CORS(app, resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})

    # JWT для аутентификации
    jwt.init_app(app)

    # SQLAlchemy для работы с БД
    db.init_app(app)

    # Flask-Migrate для миграций
    migrate.init_app(app, db)

    # Обработчики ошибок
    register_error_handlers(app)

    # Маршруты (Blueprint)
    app.register_blueprint(routes.bp)

    # Настройка логирования
    if not app.debug:
        log_dir = Path(app.root_path).parent / 'logs'
        log_dir.mkdir(exist_ok=True)

        file_handler = RotatingFileHandler(
            log_dir / 'app.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(app.config.get('LOG_LEVEL', 'INFO'))
        app.logger.addHandler(file_handler)

    app.logger.setLevel(app.config.get('LOG_LEVEL', 'INFO'))
    app.logger.info(f'Application startup with config: {config_name}')

    return app