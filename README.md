# mini_t1

Система оценки хакатонов и интеллектуальных конкурсов
**Backend** - Flask + PostgreSQL 15
**Frontend** - Angular 21 (SPA)
Инфраструктура - Docker Compose + Nginx

---

## Структура проекта

```text
c:\mini_t1
├── app/                  # Backend: Flask приложение
│   ├── admin/            # Настройки админ-панели (Flask-Admin)
│   ├── models/           # SQLAlchemy модели данных (User, Contest, Team, Grade и др.)
│   ├── routes/           # REST API endpoints (Blueprints)
│   ├── services/         # Бизнес-логика (AuthService, ContestService и др.)
│   └── utils/            # Вспомогательные утилиты, валидаторы, ошибки
├── contest-app/          # Frontend: Angular приложение
│   ├── src/app/          # Исходный код Angular
│   │   ├── core/         # Guards, Interceptors, сервисы аутентификации
│   │   ├── features/     # Модули страниц (авторизация, конкурсы, оценки и др.)
│   │   └── shared/       # Общие компоненты, модели, сервисы
│   ├── Dockerfile        # Docker-файл для dev-сборки Angular
│   └── Dockerfile.prod   # Docker-файл для prod-сборки Angular
├── migrations/           # Миграции базы данных (Alembic)
├── tests/                # Интеграционные и юнит-тесты (pytest)
├── docker-compose.yml    # Конфигурация Docker Compose для разработки
├── docker-compose.prod.yml # Конфигурация Docker Compose для продакшена
├── nginx.conf            # Конфигурация Nginx прокси
└── deploy.ps1            # PowerShell скрипт для деплоя на сервер
```

---

## Быстрый старт (локальная разработка)

### 1. Настрой окружение

```bash
copy .env.example .env
```

**Обязательно замени:**
- `SECRET_KEY` - сгенерируй: `python -c "import secrets; print(secrets.token_hex(32))"`
- `JWT_SECRET_KEY` - сгенерируй так же

### 2. Запусти через Docker

```bash
docker-compose up --build
```

**Сервисы будут доступны:**

| Сервис | URL |
|--------|-----|
| Frontend (Angular, dev-сервер) | `http://localhost:4200` |
| Backend (Flask API) | `http://localhost:5000` |
| Nginx (прокси, статика) | `http://localhost:8080` |
| Swagger UI | `http://localhost:5000/apidocs/` |
| Админ-панель | `http://localhost:5000/admin` |

### 3. Примени миграции

```bash
docker-compose exec web flask db upgrade
```

### 4. Генерация демо-данных (только локально)

Для быстрой проверки работы системы вы можете сгенерировать готовый хакатон с командами, экспертами и оценками:

```bash
docker-compose exec web flask seed-demo
```

После выполнения команды в системе появятся:
- **Организатор:** `organizer@test.ru` (Пароль: `Test1234!`)
- **Эксперты:** `expert1@test.ru`, `expert2@test.ru` (Пароль: `Test1234!`)
- Демо-хакатон (доступ по ключу `demo-key-123`) с заполненными командами, критериями и оценками Откройте его на странице организатора или посмотрите автоматически сформированный рейтинг

---

## Пользовательские сценарии

### Сценарий Организатора
1. Регистрируется и авторизуется в системе (с ролью Организатор)
2. Создает новый конкурс (указывает даты, логотип, название)
3. Добавляет в конкурс команды участников и настраивает критерии оценивания
4. Генерирует ключ доступа (Access Key) и передает его экспертам
5. Отслеживает ход оценивания и просматривает автоматически формируемый рейтинг команд
6. По окончании голосования может завершить конкурс (Finalize), зафиксировав результаты

### Сценарий Эксперта
1. Регистрируется и авторизуется в системе (с ролью Эксперт)
2. В личном кабинете вводит ID конкурса и полученный от организатора ключ доступа
3. Переходит к оцениванию команд назначенного конкурса
4. Просматривает список команд и выставляет баллы с комментариями по каждому критерию
5. Может возвращаться и редактировать свои оценки до момента закрытия конкурса организатором

---

## Деплой на сервер (продакшн)

Используется файл `docker-compose.prod.yml` и скрипт `deploy.ps1` (PowerShell)

```powershell
# Из корня проекта
.\deploy.ps1
```

Скрипт делает следующее:
1. Упаковывает проект в `project.tar.gz` (исключая `.git`, `node_modules`, кеши)
2. Загружает архив на сервер по SSH + SCP
3. Разворачивает через `docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build`

**Настройки деплоя** задаются внутри `deploy.ps1`:
- `$SERVER_IP` - IP-адрес продакшн-сервера
- `$USER` - SSH-пользователь на сервере
- `$REMOTE_DIR` - директория проекта на сервере (например `~/mini_t1_prod`)
- `$SSH_KEY` - путь к SSH-ключу (например `.\ssh\<key-name>`)

В продакшн-конфигурации (`docker-compose.prod.yml`):
- Nginx слушает порт `80`
- Frontend собирается в статику (`Dockerfile.prod`) и раздаётся через Nginx
- Исходный код не монтируется в контейнер (`./:/app` убрано)
- Используется `.env.prod`

---

## Запуск отдельных сервисов

```bash
# Только фронтенд
docker-compose up frontend --build

# Только бэкенд + база данных
docker-compose up web db --build

# Только база данных
docker-compose up db

# Все сервисы в фоновом режиме
docker-compose up -d

# Остановить все
docker-compose down

# Остановить всё с удалением базы данных
docker-compose down -v
```

---

## Конфигурация окружения

Все параметры задаются через `.env` (разработка) или `.env.prod` (продакшн).

| Переменная | Описание | Пример |
|------------|----------|--------|
| `FLASK_CONFIG` | Конфигурация приложения | `development` / `production` |
| `SECRET_KEY` | Секрет Flask-сессий | `<random_hex_32>` |
| `JWT_SECRET_KEY` | Секрет JWT | `<random_hex_32>` |
| `DATABASE_URL` | Строка подключения к PostgreSQL | `postgresql://user:pass@db:5432/db_name` |
| `DB_NAME` | Имя базы данных | `hackathon_db` |
| `DB_USER` | Пользователь БД | `postgres` |
| `DB_PASSWORD` | Пароль БД | `<strong_password>` |
| `LOG_LEVEL` | Уровень логирования | `DEBUG` / `INFO` / `WARNING` |
| `CORS_ORIGINS` | Разрешённые origin (через запятую) | `http://localhost:4200` |
| `UPLOAD_FOLDER` | Путь для загрузок внутри контейнера | `/app/uploads` |
| `UPLOADS_URL` | Публичный URL-префикс для файлов (через Nginx) | `/uploads` |
| `MAX_CONTENT_LENGTH` | Лимит загрузки Flask (байт) | `16777216` (16 MB) |
| `MAX_LOGO_SIZE` | Бизнес-лимит размера логотипа (байт) | `5242880` (5 MB) |
| `ALLOWED_EXTENSIONS` | Допустимые расширения файлов | `png,jpg,jpeg,gif,webp` |
| `SMTP_HOST` | SMTP-сервер для отправки писем | `smtp.yandex.ru` |
| `SMTP_PORT` | SMTP-порт | `465` (SSL) / `587` (TLS) |
| `SMTP_USER` | SMTP-логин | `you@yandex.ru` |
| `SMTP_PASSWORD` | SMTP-пароль | |

---

## Модели данных

| Модель | Таблица | Описание |
|--------|---------|----------|
| `User` | `users` | Организаторы и эксперты. Роль: `organizer` / `expert` |
| `Contest` | `contests` | Конкурс/хакатон. Поля: название, описание, даты, логотип, статус, `access_key` |
| `Team` | `teams` | Команда участников, привязана к конкурсу |
| `Criterion` | `criteria` | Критерий оценивания с полем `max_score`, привязан к конкурсу |
| `Grade` | `grades` | Оценка эксперта: команда x критерий. Содержит `value` и опциональный `comment` (до 3000 символов) |
| `ContestExpert` | `contest_experts` | M2M: назначение эксперта на конкурс |
| `SuperUser` | `super_users` | Суперпользователь только для Flask-Admin |

### Статусы конкурса

| Флаг | Значение |
|------|----------|
| `is_finished=False`, `is_reopened=False` | Активный конкурс, оценки принимаются |
| `is_finished=True`, `is_reopened=False` | Завершён (вручную или автоматически) |
| `is_finished=False`, `is_reopened=True` | Переоткрыт - оценки редактируются, автозавершение отключено |

**Автозавершение** происходит при обращении к конкурсу если:
- Установлена `end_date` и текущее время > `end_date`, **или**
- Нет `end_date` и все эксперты выставили все оценки (`teams x criteria x experts`)

### Access Key (ключ доступа к конкурсу)

Поле `access_key` у конкурса - необязательный уникальный ключ (строка до 64 символов).
Эксперты используют его в личном кабинете для самостоятельного присоединения к конкурсу.

---

## JWT токены

| Токен | Время жизни |
|-------|------------|
| `access_token` | 1 час (3600 сек) |
| `refresh_token` | 30 дней |

Токены передаются в заголовке: `Authorization: Bearer <token>`.
Также поддерживается query-параметр: `?token=<access_token>`.

---

## API Endpoints

Базовый префикс: `/api`

### Сервисные

| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| GET | `/api/status` | Статус сервера + версия | - |
| GET | `/api/home` | Данные главной страницы | optional JWT |

### Auth (Аутентификация)

| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| POST | `/api/auth/register` | Регистрация пользователя (`username`, `email`, `password`, `role`) | - |
| POST | `/api/auth/login` | Вход, возвращает `access_token` + `refresh_token` | - |
| POST | `/api/auth/logout` | Выход (клиент должен удалить оба токена) | JWT |
| GET | `/api/auth/me` | Данные текущего пользователя | JWT |
| POST | `/api/auth/refresh` | Обновление access-токена по refresh-токену | Refresh JWT |
| POST | `/api/auth/forgot-password` | Запрос сброса пароля - отправляет письмо со ссылкой | - |
| POST | `/api/auth/reset-password` | Сброс пароля по токену (`token`, `new_password`) | - |

> В режиме DEBUG (`forgot-password`) токен сброса также возвращается в теле ответа для удобства тестирования без почты. Токен действителен 1 час.

### Contests (Конкурсы)

| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| POST | `/api/contests` | Создать конкурс (JSON или `multipart/form-data` с логотипом) | JWT + organizer |
| GET | `/api/contests` | Список конкурсов с пагинацией (`?page=1&per_page=10&organizer_id=N`) | optional JWT |
| GET | `/api/contests/<id>` | Детали конкурса | optional JWT |
| PUT | `/api/contests/<id>` | Обновить конкурс | JWT + organizer (owner) |
| DELETE | `/api/contests/<id>` | Удалить конкурс (cascade: команды, критерии, оценки, назначения) | JWT + organizer (owner) |
| POST | `/api/contests/<id>/finalize` | Завершить голосование вручную | JWT + organizer (owner) |
| POST | `/api/contests/<id>/reopen` | Переоткрыть завершённый конкурс для пересмотра оценок | JWT + organizer (owner) |
| GET | `/api/contests/<id>/voting-status` | Статус голосования (ожидаемые/фактические оценки) | JWT |

> Завершённый конкурс (`is_finished=True`) нельзя удалить.

### Teams (Команды)

| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| POST | `/api/contests/<contest_id>/teams` | Создать команду в конкурсе | JWT + organizer |
| GET | `/api/contests/<contest_id>/teams` | Список команд конкурса с пагинацией | optional JWT |
| GET | `/api/teams/<id>` | Детали команды | optional JWT |
| PUT | `/api/teams/<id>` | Обновить команду | JWT + organizer (owner) |
| DELETE | `/api/teams/<id>` | Удалить команду (cascade: оценки) | JWT + organizer (owner) |

### Criteria (Критерии оценивания)

| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| POST | `/api/contests/<contest_id>/criteria` | Создать критерий (поля: `name`, `description`, `max_score`) | JWT + organizer |
| GET | `/api/contests/<contest_id>/criteria` | Список критериев конкурса | optional JWT |
| GET | `/api/criteria/<id>` | Детали критерия | optional JWT |
| PUT | `/api/criteria/<id>` | Обновить критерий | JWT + organizer (owner) |
| DELETE | `/api/criteria/<id>` | Удалить критерий (cascade: оценки) | JWT + organizer (owner) |

### Grades (Оценки)

| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| POST | `/api/grades` | Выставить оценку (поля: `team_id`, `criterion_id`, `value`, `comment`) | JWT + expert |
| GET | `/api/teams/<team_id>/grades` | Оценки команды | JWT (expert/organizer) |
| GET | `/api/experts/<expert_id>/grades` | Оценки конкретного эксперта | JWT + expert (owner) |
| PUT | `/api/grades/<id>` | Обновить оценку (`value`, `comment`) | JWT + expert (owner) |
| DELETE | `/api/grades/<id>` | Удалить оценку | JWT + expert (owner) |

**Правила выставления оценок:**
- Эксперт должен быть назначен на конкурс (`ContestExpert`)
- Нельзя поставить оценку дважды (команда + критерий уникальны для каждого эксперта)
- Значение `value` не может превышать `max_score` критерия
- Нельзя выставлять/редактировать оценки в завершённом конкурсе
- Просмотр оценок команды: эксперт видит все оценки (если назначен на конкурс), организатор - все (если владелец конкурса)

### Ranking (Рейтинг)

| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| GET | `/api/contests/<contest_id>/ranking` | Рейтинг команд с пагинацией (`?sort_order=desc&page=1&per_page=10`) | optional JWT |
| GET | `/api/contests/<contest_id>/teams/<team_id>/scores` | Средние оценки команды по каждому критерию | optional JWT |

**Формула подсчёта рейтинга:**

Для каждой команды:
1. По каждому критерию вычисляется **среднее арифметическое** оценок всех экспертов
2. Средние по всем критериям **суммируются**, что дает **итоговый балл** команды
3. Команды сортируются по итоговому баллу по убыванию

*Пример (2 эксперта, 3 критерия с максимальной оценкой 10):*
- *Критерий 1:* эксперт A = 8, эксперт B = 6 -> среднее = 7.0
- *Критерий 2:* эксперт A = 9, эксперт B = 7 -> среднее = 8.0
- *Критерий 3:* эксперт A = 5, эксперт B = 9 -> среднее = 7.0
**Итоговый балл команды = 7.0 + 8.0 + 7.0 = 22.0**

### Expert Assignments (Назначение экспертов)

| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| POST | `/api/contests/<contest_id>/experts` | Назначить эксперта на конкурс | JWT + organizer |
| GET | `/api/contests/<contest_id>/experts` | Список экспертов конкурса | JWT |
| GET | `/api/experts/me/contests` | Конкурсы текущего эксперта | JWT + expert |
| DELETE | `/api/contests/<contest_id>/experts/<expert_id>` | Снять эксперта с конкурса | JWT + organizer |

### Admin

| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| GET | `/admin/*` | Flask-Admin веб-интерфейс | Session Cookie (Flask-Login) |

---

## API Documentation (Swagger)

| | URL |
|-|-----|
| Swagger UI | `http://localhost:5000/apidocs/` |
| OpenAPI JSON | `http://localhost:5000/apispec_1.json` |

В Swagger UI можно авторизоваться через кнопку **Authorize** (формат: `Bearer <token>`)

---

## Админ-панель

### Доступ

| Параметр | Значение |
|----------|----------|
| URL | `http://localhost:5000/admin` |
| Аутентификация | Session Cookie (Flask-Login) |

### Создание суперпользователя

```bash
docker-compose exec web flask create-superuser
```

Суперпользователи хранятся в изолированной таблице `super_users` и не имеют доступа к API.

### Разделы

| Раздел | Описание |
|--------|----------|
| Суперпользователи | Управление доступом к админке (только просмотр) |
| Пользователи | Организаторы и эксперты системы |
| Конкурсы | Хакатоны и конкурсы |
| Команды | Команды участников |
| Критерии | Критерии оценивания |
| Оценки | Оценки экспертов |
| Назначения экспертов | M2M: эксперт <-> конкурс |

### Безопасность

- Таблица `super_users` изолирована от `users`
- Нет API-endpoint для создания SuperUser
- Блокировка после 5 неудачных попыток входа (30 минут)
- Session Cookie: `HttpOnly + Secure + SameSite=Lax`
- Все действия логируются

```bash
# Посмотреть суперпользователей
docker-compose exec db psql -U postgres -d hackathon_db -c "SELECT id, username, email, is_active FROM super_users;"

# Сбросить блокировку
docker-compose exec db psql -U postgres -d hackathon_db -c "UPDATE super_users SET failed_attempts=0, locked_until=NULL WHERE username='admin';"
```

---

## Загрузка файлов (логотипы конкурсов)

- Принимаются форматы: `png`, `jpg`, `jpeg`, `gif`, `webp`
- Максимальный размер файла: **5 MB** (бизнес-лимит), лимит Flask - 16 MB
- Хранятся в `./uploads/logos/` (монтируется в контейнер)
- Раздаются через Nginx по URL `/uploads/logos/<filename>` и `/logos/<filename>`
- При обновлении/удалении конкурса старый логотип удаляется с диска

---

## Frontend (Angular)

**Версия:** Angular 21 | TypeScript 5.9

### Страницы и маршруты

| Маршрут | Компонент | Guard |
|---------|-----------|-------|
| `/` | `ContestListComponent` | - |
| `/login` | `Login` | - |
| `/register` | `Register` | - |
| `/forgot-password` | `ForgotPassword` | - |
| `/reset-password` | `ResetPassword` | - |
| `/password-reset-sent` | `PasswordResetSent` | - |
| `/contests/:id` | `ContestDetailsPage` | - |
| `/contests/:contestId/participants` | `ParticipantsPage` | - |
| `/contests/:contestId/teams/:teamId` | `TeamScoresPage` | - |
| `/evaluation` | `EvaluationPage` | `expertGuard`, `expertEvaluationGuard` |
| `/create-contest` | `CreateContestPage` | `organizerGuard` |
| `/contest/:id/edit` | `EditContestPage` | `organizerGuard` |
| `/account/expert` | `ExpertAccountPage` | `expertGuard` |
| `/account/organizer` | `OrganizerAccountPage` | `organizerGuard` |
| `/contest-created` | `ContestCreatedPage` | - |
| `/**` | редирект на `/404` | - |

### Локальный запуск фронтенда (без Docker)

```bash
cd contest-app
npm install
npm start          # ng serve с proxy на localhost:5000
```

---

## Тесты

Тесты расположены в директории `tests/` и запускаются через `pytest`.

```bash
# Запустить все тесты
docker-compose exec web pytest

# С подробным выводом
docker-compose exec web pytest -v

# Конкретный файл
docker-compose exec web pytest tests/test_auth.py
```

**Покрытие тестами:**
- `test_auth.py` - регистрация, вход, me
- `test_contests.py` - CRUD конкурсов
- `test_contest_reopen.py` - finalize / reopen логика
- `test_grades_ranking.py` - оценки и рейтинг
- `test_expert_flow.py` - полный сценарий эксперта
- `test_teams_criteria.py` - команды и критерии
- `test_models_user.py` - юнит-тесты модели User
- `test_health.py` - `/api/status`

Тесты используют отдельную базу данных (`hackathon_test`), задаётся через `TEST_DATABASE_URL`.

---

## Миграции

```bash
# Создать новую миграцию (после изменения моделей)
docker-compose exec web flask db migrate -m "Описание изменений"

# Применить миграции
docker-compose exec web flask db upgrade

# Откатить миграцию
docker-compose exec web flask db downgrade

# Проверить таблицы в БД
docker-compose exec db psql -U postgres -d hackathon_db -c "\dt"
```

---

## Основные команды

| Команда | Описание |
|---------|----------|
| `docker-compose up --build` | Собрать и запустить все сервисы |
| `docker-compose up -d` | Запустить все в фоне |
| `docker-compose down` | Остановить все сервисы |
| `docker-compose down -v` | Остановить + удалить volume БД |
| `docker-compose exec web flask db upgrade` | Применить миграции |
| `docker-compose exec web flask db migrate -m "..."` | Создать миграцию |
| `docker-compose exec web flask create-superuser` | Создать суперпользователя |
| `docker-compose exec web pytest` | Запустить тесты |
| `.\deploy.ps1` | Деплой на продакшн-сервер |
| `.\push_to_sfera.ps1` | Синхронизировать все ветки с remote `sfera` |

---

## Стек технологий

| Слой | Технология |
|------|-----------|
| Backend | Python 3.11 + Flask 3.0 |
| Database | PostgreSQL 15 |
| ORM | SQLAlchemy 3 (Flask-SQLAlchemy) |
| Migrations | Alembic (Flask-Migrate) |
| Auth API | JWT (Flask-JWT-Extended) |
| Auth Admin | Session Cookie (Flask-Login) |
| Admin Panel | Flask-Admin |
| API Docs | Flasgger (Swagger UI / OpenAPI) |
| Email | Flask-Mail (SMTP) |
| Frontend | Angular 21 |
| Frontend build | Angular CLI 21 |
| Proxy | Nginx (alpine) |
| Containerization | Docker + Docker Compose |
| Testing | pytest |
