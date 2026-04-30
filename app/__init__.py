import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from app.config import config
from app.extensions import db, migrate, jwt
from app.jwt_config import init_jwt
from app.admin import init_admin
from app.extensions import login_manager
from app.cli import init_cli
from app import routes
from app.utils.errors import register_error_handlers, register_jwt_error_handlers


def create_app(config_name=None):
    """Factory function для создания Flask приложения"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Создаём папку uploads при старте, если её нет
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder:
        Path(upload_folder).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(upload_folder, 'logos')).mkdir(parents=True, exist_ok=True)

    # CORS для Angular
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', '*'),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # JWT для аутентификации - явно устанавливаем секрет перед инициализацией
    if not app.config.get('JWT_SECRET_KEY'):
        app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key-for-jwt')
    
    jwt.init_app(app)
    register_jwt_error_handlers(jwt)

    # Swagger документация
    app.config['SWAGGER'] = {
        'title': 'Hackathon Evaluation System API',
        'uiversion': 3,
        'version': '1.0.0',
        'description': 'API для системы оценки результатов хакатонов и интеллектуальных конкурсов',
        'contact': {
            'name': 'Development Team'
        }
    }
    app.config['SWAGGER_UI_DOC_EXPANSION'] = 'list'

    # Swagger спецификация
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header. Пример: Bearer <token>"
            }
        }
    }

    Swagger(app, config=swagger_config)

    # SQLAlchemy для работы с БД
    db.init_app(app)

    # Flask-Migrate для миграций
    migrate.init_app(app, db)

    # Инициализация админки
    init_admin(app)

    # Инициализация CLI команд
    init_cli(app)

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
    app.logger.info(f'Upload folder: {upload_folder}')

    return app