from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pathlib import Path

from app.config import Config
from app.extensions import db, migrate
from app import routes


def create_app():
    """
    Factory function для создания Flask приложения и инициализации бд
    """

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Если DATABASE_URL не задана, используем SQLite в instance/app.db
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        Path(app.instance_path).mkdir(parents=True, exist_ok=True)
        db_path = Path(app.instance_path) / "app.db"
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    # Инициализация CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Инициализация JWT менеджера
    jwt = JWTManager()
    jwt.init_app(app)

    # Инициализация SQLAlchemy
    db.init_app(app)

    # Инициализация Flask-Migrate 
    migrate.init_app(app, db)

    # Регистрация Blueprint (маршруты)
    app.register_blueprint(routes.bp)

    return app