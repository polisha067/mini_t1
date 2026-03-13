import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Конфигурация приложения Flask"""

    # Секретный ключ для подписи cookie и сессий
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-secret-key'

    # Секретный ключ специально для JWT токенов
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'fallback-jwt-key'

    # Время жизни access токена
    JWT_ACCESS_TOKEN_EXPIRES = 3600

    # Режим отладки
    DEBUG = os.environ.get('FLASK_DEBUG') == 'True'

    # Настройки базы данных, если DATABASE_URL не задана, то путь к SQLite зададется в create_app()
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False