import click
import os
import random
from datetime import datetime, timedelta, UTC
from flask.cli import with_appcontext
from flask import current_app
from app.extensions import db
from app.models.super_user import SuperUser
from app.models.user import User
from app.models.contest import Contest
from app.models.team import Team
from app.models.criterion import Criterion
from app.models.contest_expert import ContestExpert
from app.models.grade import Grade

@click.command('create-superuser')
@click.option('--username', prompt=True, help='Логин суперпользователя')
@click.option('--email', prompt=True, help='Email суперпользователя')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Пароль')
@with_appcontext
def create_superuser(username, email, password):
    """ Создать суперпользователя для доступа к админке"""
    existing = SuperUser.query.filter_by(username=username).first()
    if existing:
        click.echo(f'Суперпользователь {username} уже существует!')
        return

    existing_email = SuperUser.query.filter_by(email=email).first()
    if existing_email:
        click.echo(f'Email {email} уже используется!')
        return

    superuser = SuperUser(
        username=username,
        email=email,
        is_active=True
    )
    superuser.set_password(password)

    db.session.add(superuser)
    db.session.commit()

    click.echo(f'✅ Суперпользователь создан:')
    click.echo(f'   Логин: {username}')
    click.echo(f'   Email: {email}')
    click.echo(f'   URL: http://localhost:5000/admin')
    click.echo(f'   ⚠️  Запомните пароль - восстановить нельзя!')


@click.command('seed-demo')
@with_appcontext
def seed_demo():
    """Сгенерировать демо-данные (только для локальной разработки)"""

    
    # Проверяем, что не в продакшене
    flask_config = os.environ.get('FLASK_CONFIG', 'development')
    if flask_config == 'production' or not current_app.config.get('DEBUG'):
        click.echo("⚠️  Генерация демо-данных запрещена в production-окружении!")
        return

    # Создаем организатора
    org = User.query.filter_by(email='organizer@test.ru').first()
    if not org:
        org = User(username='Demo Organizer', email='organizer@test.ru', role='organizer')
        org.set_password('Test1234!')
        db.session.add(org)
        
    # Создаем экспертов
    exp1 = User.query.filter_by(email='expert1@test.ru').first()
    if not exp1:
        exp1 = User(username='Demo Expert 1', email='expert1@test.ru', role='expert')
        exp1.set_password('Test1234!')
        db.session.add(exp1)

    exp2 = User.query.filter_by(email='expert2@test.ru').first()
    if not exp2:
        exp2 = User(username='Demo Expert 2', email='expert2@test.ru', role='expert')
        exp2.set_password('Test1234!')
        db.session.add(exp2)

    db.session.commit()

    # Создаем конкурс
    contest = Contest.query.filter_by(name='Демо Хакатон').first()
    if not contest:
        contest = Contest(
            name='Демо Хакатон',
            description='Автоматически сгенерированный хакатон для демонстрации.',
            start_date=datetime.now(UTC) - timedelta(days=1),
            end_date=datetime.now(UTC) + timedelta(days=5),
            organizer_id=org.id,
            access_key='demo-key-123'
        )
        db.session.add(contest)
        db.session.commit()

        # Создаем команды
        teams = []
        for i in range(1, 4):
            team = Team(name=f'Команда {i}', description=f'Описание команды {i}', contest_id=contest.id)
            db.session.add(team)
            teams.append(team)

        # Создаем критерии
        criteria = []
        for i in range(1, 4):
            crit = Criterion(name=f'Критерий {i}', description=f'Описание критерия {i}', max_score=10, contest_id=contest.id)
            db.session.add(crit)
            criteria.append(crit)

        db.session.commit()

        # Назначаем экспертов
        ce1 = ContestExpert(contest_id=contest.id, user_id=exp1.id)
        ce2 = ContestExpert(contest_id=contest.id, user_id=exp2.id)
        db.session.add_all([ce1, ce2])
        db.session.commit()

        # Проставляем оценки
        for team in teams:
            for crit in criteria:
                # Эксперт 1 оценивает
                g1 = Grade(expert_id=exp1.id, team_id=team.id, criterion_id=crit.id, value=random.randint(5, 10))
                # Эксперт 2 оценивает
                g2 = Grade(expert_id=exp2.id, team_id=team.id, criterion_id=crit.id, value=random.randint(5, 10))
                db.session.add_all([g1, g2])
        
        db.session.commit()
        click.echo("✅ Демо-данные успешно сгенерированы!")
        click.echo("Организатор: organizer@test.ru / Test1234!")
        click.echo("Эксперты: expert1@test.ru, expert2@test.ru / Test1234!")
        click.echo("Ключ для конкурса: demo-key-123")
    else:
        click.echo("ℹ️ Демо-конкурс уже существует")


def init_cli(app):
    """Регистрация CLI команд"""
    app.cli.add_command(create_superuser)
    app.cli.add_command(seed_demo)