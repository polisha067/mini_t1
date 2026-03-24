import click
from flask.cli import with_appcontext
from app.extensions import db
from app.models.super_user import SuperUser


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


def init_cli(app):
    """Регистрация CLI команд"""
    app.cli.add_command(create_superuser)