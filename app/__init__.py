from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import Config
from app import routes

def create_app():
    """
    Factory function для создания Flask приложения
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Инициализация CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Инициализация JWT менеджера
    jwt = JWTManager()
    jwt.init_app(app)

    # Регистрация Blueprint (маршруты)
    app.register_blueprint(routes.bp)

    return app