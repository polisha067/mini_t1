from flask import redirect, url_for, request, flash, render_template
from flask_login import login_user, logout_user, login_required, current_user
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from wtforms import PasswordField, SelectField
from app.models.super_user import SuperUser
from app.models.user import User
from app.models.contest import Contest
from app.models.team import Team
from app.models.criterion import Criterion
from app.models.grade import Grade
from app.models.contest_expert import ContestExpert
from app.extensions import db
from datetime import datetime
import secrets

# Импортируем существующие валидаторы
from app.utils.validators.user import validate_user_role
from app.utils.validators.contest import validate_contest_data, validate_score


class SecureAdminIndexView(AdminIndexView):
    """Защищённая главная страница админки"""

    @expose('/')
    @login_required
    def index(self):
        return self.render('admin/index.html')

    @expose('/login', methods=['GET', 'POST'])
    def login(self):
        """Страница входа в админку"""
        if current_user.is_authenticated:
            return redirect(url_for('admin.index'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            remember = request.form.get('remember', False)

            if not username or not password:
                flash('Введите логин и пароль', 'danger')
                return self.render('admin/login.html')

            user = SuperUser.query.filter_by(username=username).first()

            if user and user.check_password(password):
                login_user(user, remember=remember)
                flash(f'Добро пожаловать, {user.username}!', 'success')

                next_page = request.args.get('next')
                return redirect(next_page or url_for('admin.index'))
            else:
                flash('Неверный логин или пароль', 'danger')

        return self.render('admin/login.html')

    @expose('/logout')
    @login_required
    def logout(self):
        """Выход из админки"""
        logout_user()
        flash('Вы успешно вышли', 'info')
        return redirect(url_for('admin.login'))


class BaseModelView(ModelView):
    """Базовый view с проверкой авторизации"""

    def is_accessible(self):
        """Проверка доступа - только авторизованные SuperUser"""
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        """Действие при отсутствии доступа"""
        flash('Требуется авторизация администратора', 'warning')
        return redirect(url_for('admin.login', next=request.url))

    # Глобальные настройки на русском
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    # Тексты кнопок
    create_button = 'Создать'
    edit_button = 'Редактировать'
    delete_button = 'Удалить'
    details_button = 'Просмотр'

    # Сообщения
    delete_confirmation = 'Вы уверены что хотите удалить эту запись?'

    # Пагинация
    page_size = 20
    can_export = True
    export_types = ['csv', 'excel']


class SuperUserAdmin(BaseModelView):
    """Админка для суперпользователей"""

    # Только просмотр для безопасности
    can_create = False
    can_edit = True
    can_delete = False

    column_list = ('id', 'username', 'email', 'is_active', 'created_at', 'last_login')
    column_searchable_list = ('username', 'email')
    column_filters = ('is_active', 'created_at')
    column_editable_list = ('is_active',)

    form_columns = ('username', 'email', 'is_active')
    form_excluded_columns = ('password_hash', 'created_at', 'last_login', 'failed_attempts', 'locked_until')

    # Все подписи на русском
    column_labels = {
        'id': 'ID',
        'username': 'Логин',
        'email': 'Email',
        'is_active': 'Активен',
        'created_at': 'Дата создания',
        'last_login': 'Последний вход',
        'failed_attempts': 'Неудачные попытки',
        'locked_until': 'Заблокирован до'
    }

    # Заголовки столбцов
    column_descriptions = {
        'username': 'Логин для входа в админку',
        'email': 'Контактный email',
        'is_active': 'Активен ли пользователь'
    }

    # Названия страницы
    name = 'Суперпользователи'
    verbose_name = 'Суперпользователь'
    verbose_name_plural = 'Суперпользователи'


class UserAdmin(BaseModelView):
    """Админка для обычных пользователей"""

    column_list = ('id', 'username', 'email', 'role', 'created_at')
    column_searchable_list = ('username', 'email')
    column_filters = ('role', 'created_at')
    column_editable_list = ('role',)

    form_columns = ('username', 'email', 'role', 'password')
    form_excluded_columns = ('password_hash', 'created_at', 'contests', 'grades', 'contest_assignments')

    # Поле пароля
    form_extra_fields = {
        'password': PasswordField('Пароль', description='Минимум 6 символов, буквы и цифры'),
        'role': SelectField('Роль', choices=[
            ('organizer', 'Организатор'),
            ('expert', 'Эксперт')
        ], description='Выберите роль пользователя')
    }

    # Все подписи на русском
    column_labels = {
        'id': 'ID',
        'username': 'Имя пользователя',
        'email': 'Email',
        'role': 'Роль',
        'password': 'Пароль',
        'created_at': 'Дата создания'
    }

    # Названия страницы
    name = 'Пользователи'
    verbose_name = 'Пользователь'
    verbose_name_plural = 'Пользователи'

    def on_model_change(self, form, model, is_created):
        """Хэширование пароля при создании/изменении"""
        if hasattr(form, 'password') and form.password.data:
            model.set_password(form.password.data)
        super().on_model_change(form, model, is_created)


class ContestAdmin(BaseModelView):
    """Админка для конкурсов"""

    column_list = ('id', 'name', 'organizer', 'start_date', 'end_date', 'logo_path', 'created_at')
    column_searchable_list = ('name', 'description')
    column_filters = ('start_date', 'end_date', 'organizer_id')

    form_columns = ('name', 'description', 'start_date', 'end_date', 'logo_path', 'organizer_id')
    form_excluded_columns = ('teams', 'criteria', 'assigned_experts')

    # Фильтруем только организаторов в dropdown
    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.organizer_id.query_factory = lambda: User.query.filter_by(role='organizer')
        return form

    # Все подписи на русском
    column_labels = {
        'id': 'ID',
        'name': 'Название конкурса',
        'description': 'Описание',
        'start_date': 'Дата начала',
        'end_date': 'Дата окончания',
        'logo_path': 'Путь к логотипу',
        'created_at': 'Дата создания',
        'organizer_id': 'ID организатора'
    }

    form_args = {
        'name': {
            'label': 'Название конкурса',
            'description': 'От 3 до 200 символов'
        },
        'description': {
            'label': 'Описание',
            'description': 'Подробное описание конкурса (необязательно)'
        },
        'start_date': {
            'label': 'Дата начала',
            'description': 'Формат: ГГГГ-ММ-ДД ЧЧ:ММ'
        },
        'end_date': {
            'label': 'Дата окончания',
            'description': 'Должна быть позже даты начала'
        },
        'logo_path': {
            'label': 'Путь к логотипу',
            'description': 'Путь к файлу логотипа (например: /static/logos/contest.png)'
        },
        'organizer_id': {
            'label': 'ID организатора',
            'description': 'Выберите существующего пользователя-организатора'
        }
    }

    # Названия страницы
    name = 'Конкурсы'
    verbose_name = 'Конкурс'
    verbose_name_plural = 'Конкурсы'

    def on_model_change(self, form, model, is_created):
        """Валидация данных конкурса с использованием существующих валидаторов"""
        # Валидация данных конкурса
        contest_data = {
            'name': form.name.data,
            'description': form.description.data,
            'start_date': form.start_date.data.isoformat() if form.start_date.data else None,
            'end_date': form.end_date.data.isoformat() if form.end_date.data else None,
        }

        valid, error = validate_contest_data(contest_data)
        if not valid:
            flash(f'Ошибка валидации: {error}', 'danger')
            raise ValueError(error)

        # Проверка что организатор имеет роль 'organizer'
        organizer = User.query.get(model.organizer_id)
        if not organizer:
            flash('Организатор не найден', 'danger')
            raise ValueError('Организатор не найден')

        valid, error = validate_user_role(organizer.role)
        if not valid or organizer.role != 'organizer':
            flash(f'Пользователь {organizer.username} не является организатором (роль: {organizer.role})', 'danger')
            raise ValueError('Только пользователь с ролью "organizer" может быть организатором конкурса')

        super().on_model_change(form, model, is_created)


class TeamAdmin(BaseModelView):
    """Админка для команд"""

    column_list = ('id', 'name', 'contest', 'description', 'created_at')
    column_searchable_list = ('name', 'description')
    column_filters = ('contest_id', 'created_at')

    form_columns = ('name', 'description', 'contest_id')
    form_excluded_columns = ('grades',)

    # Все подписи на русском
    column_labels = {
        'id': 'ID',
        'name': 'Название команды',
        'description': 'Описание',
        'contest': 'Конкурс',
        'contest_id': 'ID конкурса',
        'created_at': 'Дата создания'
    }

    form_args = {
        'name': {
            'label': 'Название команды',
            'description': 'Уникальное название команды'
        },
        'description': {
            'label': 'Описание команды',
            'description': 'Краткое описание команды (состав, проект)'
        },
        'contest_id': {
            'label': 'ID конкурса',
            'description': 'Выберите конкурс к которому принадлежит команда'
        }
    }

    # Названия страницы
    name = 'Команды'
    verbose_name = 'Команда'
    verbose_name_plural = 'Команды'


class CriterionAdmin(BaseModelView):
    """Админка для критериев"""

    column_list = ('id', 'name', 'contest', 'max_score', 'description')
    column_searchable_list = ('name', 'description')
    column_filters = ('contest_id', 'max_score')

    form_columns = ('name', 'description', 'max_score', 'contest_id')
    form_excluded_columns = ('grades',)

    # Все подписи на русском
    column_labels = {
        'id': 'ID',
        'name': 'Название критерия',
        'description': 'Описание',
        'max_score': 'Максимальный балл',
        'contest': 'Конкурс',
        'contest_id': 'ID конкурса'
    }

    form_args = {
        'name': {
            'label': 'Название критерия',
            'description': 'Например: "Код", "Презентация", "Инновации"'
        },
        'description': {
            'label': 'Описание критерия',
            'description': 'Подробное описание что оценивается'
        },
        'max_score': {
            'label': 'Максимальный балл',
            'description': 'Обычно 10'
        },
        'contest_id': {
            'label': 'ID конкурса',
            'description': 'Выберите конкурс к которому относится критерий'
        }
    }

    # Названия страницы
    name = 'Критерии'
    verbose_name = 'Критерий'
    verbose_name_plural = 'Критерии'

    def on_model_change(self, form, model, is_created):
        """Валидация максимального балла с использованием существующего валидатора"""
        valid, error = validate_score(form.max_score.data, max_score=100)
        if not valid:
            flash(f'Ошибка валидации: {error}', 'danger')
            raise ValueError(error)
        super().on_model_change(form, model, is_created)

class GradeAdmin(BaseModelView):
    """Админка для оценок"""

    column_list = ('id', 'expert', 'team', 'criterion', 'value', 'comment', 'updated_at')
    column_searchable_list = ('value', 'comment')
    column_filters = ('expert_id', 'team_id', 'criterion_id', 'value')
    column_editable_list = ('value',)

    form_columns = ('value', 'comment', 'expert_id', 'team_id', 'criterion_id')

    # Все подписи на русском
    column_labels = {
        'id': 'ID',
        'value': 'Балл',
        'comment': 'Комментарий',
        'expert': 'Эксперт',
        'team': 'Команда',
        'criterion': 'Критерий',
        'expert_id': 'ID эксперта',
        'team_id': 'ID команды',
        'criterion_id': 'ID Критерия',
        'updated_at': 'Обновлено',
        'created_at': 'Создано'
    }

    form_args = {
        'value': {
            'label': 'Балл',
            'description': 'Оценка от 0 до максимального значения критерия'
        },
        'comment': {
            'label': 'Комментарий',
            'description': 'Необязательный комментарий эксперта к оценке'
        },
        'expert_id': {
            'label': 'ID эксперта',
            'description': 'Выберите эксперта который выставил оценку'
        },
        'team_id': {
            'label': 'ID команды',
            'description': 'Выберите команду которую оценили'
        },
        'criterion_id': {
            'label': 'ID критерия',
            'description': 'Выберите критерий по которому выставлена оценка'
        }
    }

    # Названия страницы
    name = 'Оценки'
    verbose_name = 'Оценка'
    verbose_name_plural = 'Оценки'

    def on_model_change(self, form, model, is_created):
        """Валидация оценки с использованием существующего валидатора"""
        # Получаем максимальный балл из критерия
        criterion = Criterion.query.get(form.criterion_id.data)
        if criterion:
            valid, error = validate_score(form.value.data, max_score=criterion.max_score)
            if not valid:
                flash(f'Ошибка валидации: {error}', 'danger')
                raise ValueError(error)
        super().on_model_change(form, model, is_created)

class ContestExpertAdmin(BaseModelView):
    """Админка для назначения экспертов"""

    column_list = ('id', 'contest', 'expert', 'assigned_at')
    column_filters = ('contest_id', 'user_id', 'assigned_at')

    form_columns = ('contest_id', 'user_id')

    # Фильтруем только экспертов в dropdown
    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.user_id.query_factory = lambda: User.query.filter_by(role='expert')
        return form

    # Все подписи на русском
    column_labels = {
        'id': 'ID',
        'contest': 'Конкурс',
        'expert': 'Эксперт',
        'contest_id': 'ID конкурса',
        'user_id': 'ID эксперта',
        'assigned_at': 'Дата назначения'
    }

    form_args = {
        'contest_id': {
            'label': 'ID конкурса',
            'description': 'Выберите конкурс на который назначается эксперт'
        },
        'user_id': {
            'label': 'ID эксперта',
            'description': 'Выберите пользователя с ролью "Эксперт"'
        }
    }

    # Названия страницы
    name = 'Назначения экспертов'
    verbose_name = 'Назначение'
    verbose_name_plural = 'Назначения экспертов'

    def on_model_change(self, form, model, is_created):
        """Проверка что пользователь имеет роль 'expert'"""
        expert = User.query.get(model.user_id)
        if not expert:
            flash('Эксперт не найден', 'danger')
            raise ValueError('Эксперт не найден')

        valid, error = validate_user_role(expert.role)
        if not valid or expert.role != 'expert':
            flash(f'Пользователь {expert.username} не является экспертом (роль: {expert.role})', 'danger')
            raise ValueError('Только пользователь с ролью "expert" может быть назначен экспертом на конкурс')

        super().on_model_change(form, model, is_created)