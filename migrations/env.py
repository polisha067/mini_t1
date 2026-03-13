import logging
from logging.config import fileConfig
from flask import current_app
from alembic import context

# Объект конфигурации Alembic, предоставляет доступ к настройкам из .ini
config = context.config

# Настройка логгеров из конфигурационного файла
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def get_engine():
    """Получает движок базы данных из Flask-SQLAlchemy"""
    try:
        # Работает с Flask-SQLAlchemy < 3
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # Работает с Flask-SQLAlchemy >= 3
        return current_app.extensions['migrate'].db.engine


def get_engine_url():
    """Получает URL подключения к базе данных"""
    try:
        return get_engine().url.render_as_string(hide_password=False).replace('%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')


# Получаем метаданные моделей SQLAlchemy для autogenerate
target_db = current_app.extensions['migrate'].db


def get_metadata():
    """Возвращает метаданные моделей для сравнения схем"""
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata


# Устанавливаем URL базы данных в конфигурацию Alembic
config.set_main_option('sqlalchemy.url', get_engine_url())


def run_migrations_offline():
    """
    Запуск миграций в 'офлайн' режиме.
    Настраивает контекст только с URL, без создания Engine.
    Вызовы context.execute() выводят SQL в консоль.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    Запуск миграций в 'онлайн' режиме.
    Создаёт Engine и подключается к базе данных.
    """

    # Предотвращает создание миграции, если нет изменений в схеме
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('Изменений в схеме не обнаружено.')

    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args
        )

        with context.begin_transaction():
            context.run_migrations()


# Запуск в зависимости от режима
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()