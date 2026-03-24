from flask_admin import Admin
from app.extensions import db, login_manager
from .views import (
    SecureAdminIndexView,
    SuperUserAdmin,
    UserAdmin,
    ContestAdmin,
    TeamAdmin,
    CriterionAdmin,
    GradeAdmin,
    ContestExpertAdmin
)
from app.models import User, Contest, Team, Criterion, Grade, ContestExpert, SuperUser



def init_admin(app):
    """
    Инициализация Flask-Admin с защитой

    Args:
        app: Flask приложение
    """
    # Инициализация Flask-Login
    login_manager.init_app(app)

    admin = Admin(
        app,
        name='Hackathon Admin Panel',
        template_mode='bootstrap4',
        index_view=SecureAdminIndexView(name='Главная'),
        url='/admin'
    )
    # SuperUserAdmin - только просмотр (нельзя создавать/удалять через админку)
    super_user_admin = SuperUserAdmin(SuperUser, db.session, category='Доступ')
    super_user_admin.can_create = False
    super_user_admin.can_delete = False
    admin.add_view(super_user_admin)

    admin.add_view(UserAdmin(User, db.session, category='Система'))
    admin.add_view(ContestAdmin(Contest, db.session, category='Конкурсы'))
    admin.add_view(TeamAdmin(Team, db.session, category='Конкурсы'))
    admin.add_view(CriterionAdmin(Criterion, db.session, category='Конкурсы'))
    admin.add_view(GradeAdmin(Grade, db.session, category='Оценки'))
    admin.add_view(ContestExpertAdmin(ContestExpert, db.session, category='Оценки'))