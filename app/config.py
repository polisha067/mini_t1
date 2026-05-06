import os


class Config:
    """
    Базовая конфигурация приложения
    Содержит общие настройки для всех сред (dev, prod, test)
    """

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'fallback-jwt-key-change-too'

    # Время жизни access токена в секундах (1 час)
    JWT_ACCESS_TOKEN_EXPIRES = 3600

    # Время жизни refresh токена (30 дней)
    JWT_REFRESH_TOKEN_EXPIRES = 60 * 60 * 24 * 30

    # Настройки JWT - искать токен в заголовке Authorization и query параметре
    JWT_TOKEN_LOCATION = ['headers', 'query_string']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_QUERY_STRING_NAME = 'token'

    # Отключаем CSRF для API (используем только для Stateless API)
    JWT_COOKIE_CSRF_PROTECT = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 1800,
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'max_overflow': 10
    }

    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

    # URL для доступа к загруженным файлам (через Nginx)
    UPLOADS_URL = os.environ.get('UPLOADS_URL', '/uploads')

    # Папка для загруженных файлов (относительно корня проекта)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')

    # Максимальный размер загружаемого файла (16 MB - лимит Flask)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Разрешённые расширения для логотипов
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Максимальный размер файла для валидации в бизнес-логике (5 MB)
    MAX_LOGO_SIZE = 5 * 1024 * 1024


class DevelopmentConfig(Config):
    """
    Конфигурация для локальной разработки
    Включает отладку и удобные настройки для разработчика
    """
    DEBUG = True

    # PostgreSQL для разработки (локальный или в Docker)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              os.environ.get('DEV_DATABASE_URL') or \
                              'postgresql://postgres:postgres123@localhost:5432/hackathon_dev'

    LOG_LEVEL = 'DEBUG'
    PROPAGATE_EXCEPTIONS = True


class ProductionConfig(Config):
    """
    Конфигурация для продакшена
    Максимальная безопасность и производительность
    """
    DEBUG = False

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        uri = os.environ.get('DATABASE_URL')
        if not uri:
            raise RuntimeError("DATABASE_URL is required in production!")
        return uri

    PROPAGATE_EXCEPTIONS = False
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """
    Конфигурация для автоматических тестов
    Использует изолированную БД для чистоты тестов
    """
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'postgresql://postgres:postgres123@localhost:5432/hackathon_test'

    WTF_CSRF_ENABLED = False
    JWT_ACCESS_TOKEN_EXPIRES = False
    JWT_REFRESH_TOKEN_EXPIRES = False
    LOG_LEVEL = 'ERROR'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'test-secret-key-must-be-at-least-32-bytes-long')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}