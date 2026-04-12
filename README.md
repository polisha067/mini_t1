# mini_t1

Система оценки хакатонов. Backend на Flask + PostgreSQL, frontend на Angular.

---


## Быстрый старт

### 1. Настрой окружение

Скопируй `.env.example` в `.env` и заполни своими данными:

```bash
copy .env.example .env
```

**Обязательно замени:**
- `SECRET_KEY` — сгенерируй: `python -c "import secrets; print(secrets.token_hex(32))"`
- `JWT_SECRET_KEY` — сгенерируй так же

### 2. Запусти через Docker

```bash
docker-compose up --build
```

**Сервисы будут доступны:**
- Frontend (Angular): `http://localhost:4200`
- Backend (Flask API): `http://localhost:5000`

### 3. Примени миграции

```bash
docker-compose exec web flask db upgrade
```

---

## Запуск отдельных сервисов

### Только фронтенд

```bash
docker-compose up frontend --build
```

### Только бекенд + база данных

```bash
docker-compose up web db --build
```

### Только база данных

```bash
docker-compose up db
```

### Все сервисы в фоновом режиме

```bash
docker-compose up -d
```

### Остановить сервисы

```bash
# Остановить все
docker-compose down

# Остановить всё с удалением базы данных
docker-compose down -v

# Остановить только фронтенд
docker-compose stop frontend

# Остановить только бекенд
docker-compose stop web
```

---

## Админ-панель

Для управления данными через веб-интерфейс предусмотрена админ-панель.

### Доступ

| Параметр | Значение |
|----------|----------|
| **URL** | `http://localhost:5000/admin` |
| **Аутентификация** | Session Cookie (Flask-Login) |

### Создание суперпользователя

Суперпользователь создаётся только через CLI:

```bash
docker-compose exec web flask create-superuser
```

**Введите данные:**
```
Username: admin
Email: admin@hackathon.local
Password: ******
Repeat for confirmation: ******
```

### Вход в админ-панель

1. Откройте `http://localhost:5000/admin`
2. Введите логин и пароль созданные через CLI

### Разделы админ-панели

| Раздел | Описание |
|--------|----------|
| Суперпользователи | Управление доступом к админке (только просмотр) |
| Пользователи | Организаторы и эксперты системы |
| Конкурсы | Хакатоны и интеллектуальные конкурсы |
| Команды | Команды участников |
| Критерии | Критерии оценивания |
| Оценки | Оценки экспертов |
| Назначения экспертов | Назначение экспертов на конкурсы |

### Безопасность

- Отдельная таблица `super_users` (изолирована от основных пользователей)
- Нет API endpoint для создания SuperUser
- Блокировка после 5 неудачных попыток входа (30 минут)
- Session Cookie: HttpOnly + Secure + SameSite=Lax
- Все действия логируются в консоль приложения

### Полезные команды

```bash
# Посмотреть список суперпользователей
docker-compose exec db psql -U postgres -d hackathon_db -c "SELECT id, username, email, is_active FROM super_users;"

# Сбросить блокировку после неудачных попыток
docker-compose exec db psql -U postgres -d hackathon_db -c "UPDATE super_users SET failed_attempts=0, locked_until=NULL WHERE username='admin';"
```

---

## Основные команды

| Команда | Описание |
| :--- | :--- |
| `docker-compose up --build` | Собрать и запустить все сервисы |
| `docker-compose up frontend --build` | Запустить только фронтенд |
| `docker-compose up web db --build` | Запустить бекенд с базой данных |
| `docker-compose up -d` | Запустить все сервисы в фоне |
| `docker-compose down` | Остановить все сервисы |
| `docker-compose down -v` | Остановить + удалить базу данных |
| `docker-compose stop frontend` | Остановить только фронтенд |
| `docker-compose stop web` | Остановить только бекенд |
| `flask db migrate -m "Описание"` | Создать новую миграцию |
| `flask db upgrade` | Применить миграции |
| `flask db downgrade` | Откатить миграцию |
| `flask create-superuser` | Создать суперпользователя для админки |

---

## API Documentation (Swagger)

Документация API доступна через Swagger UI:

| Описание | URL |
|----------|-----|
| **Swagger UI** | `http://localhost:5000/apidocs/` |
| **API Spec (JSON)** | `http://localhost:5000/apispec_1.json` |

В Swagger UI можно:
- Просматривать все доступные endpoints
- Тестировать API прямо из браузера
- Авторизоваться через JWT токен (кнопка Authorize)

---

## API Endpoints

| Метод | Endpoint | Описание |
| :--- | :--- | :--- |
| POST | `/api/auth/register` | Регистрация пользователя |
| POST | `/api/auth/login` | Вход (получение JWT токена) |
| POST | `/api/auth/logout` | Выход (инвалидация токена) |
| GET | `/api/auth/me` | Получить текущего пользователя | JWT |

### Contests (Конкурсы)

| Метод | Endpoint | Описание | Auth |
| :--- | :--- | :--- | :--- |
| POST | `/api/contests` | Создать конкурс | JWT + organizer |
| GET | `/api/contests` | Список конкурсов (пагинация) | JWT |
| GET | `/api/contests/<id>` | Детали конкурса | JWT |
| PUT | `/api/contests/<id>` | Обновить конкурс | JWT + organizer (owner) |
| DELETE | `/api/contests/<id>` | Удалить конкурс (cascade) | JWT + organizer (owner) |

### Teams (Команды)

| Метод | Endpoint | Описание | Auth |
| :--- | :--- | :--- | :--- |
| POST | `/api/contests/<contest_id>/teams` | Создать команду | JWT + organizer |
| GET | `/api/contests/<contest_id>/teams` | Список команд конкурса (пагинация) | optional |
| GET | `/api/teams/<id>` | Детали команды | optional |
| PUT | `/api/teams/<id>` | Обновить команду | JWT + organizer (owner) |
| DELETE | `/api/teams/<id>` | Удалить команду (cascade: grades) | JWT + organizer (owner) |

### Criteria (Критерии оценивания)

| Метод | Endpoint | Описание | Auth |
| :--- | :--- | :--- | :--- |
| POST | `/api/contests/<contest_id>/criteria` | Создать критерий | JWT + organizer |
| GET | `/api/contests/<contest_id>/criteria` | Список критериев конкурса | optional |
| GET | `/api/criteria/<id>` | Детали критерия | optional |
| PUT | `/api/criteria/<id>` | Обновить критерий | JWT + organizer (owner) |
| DELETE | `/api/criteria/<id>` | Удалить критерий (cascade: grades) | JWT + organizer (owner) |

### Grade (Оценки)
| Метод | Endpoint | Описание | Auth |
| :--- | :--- | :--- | :--- |
| POST | `/api/grades` | 	Выставить оценку |JWT + expert |
| GET | `/api/teams/<team_id>/grades` | Список оценок команды | optional |
| GET | `/api/experts/<expert_id>/grades` |Список оценок эксперта |JWT + expert (owner) |
| PUT | `/api/grades/<id>` | Обновить оценку |JWT + expert (owner) |
| DELETE | `/api/grades/<id>` | Удалить оценку | 	JWT + expert (owner) |

### Ranking (Рейтинг)
| Метод | Endpoint | Описание | Auth |
| :--- | :--- | :--- | :--- |
| GET | `/api/contests/<contest_id>/ranking` | Итоговый рейтинг команд конкурса | optional |

### Expert Assignments (Назначение экспертов)
| Метод | Endpoint | Описание | Auth |
| :--- | :--- | :--- | :--- |
| POST | `/api/contests/<contest_id>/experts` | Назначить эксперта на конкурс | JWT + organizer |
| GET | `/api/contests/<contest_id>/experts` | Список экспертов конкурса | JWT |
| GET | `/api/experts/me/contests` | Мои конкурсы (для эксперта) | JWT + expert |
| DELETE | `/api/contests/<contest_id>/experts/<expert_id>` | Снять эксперта с конкурса | JWT + organizer |

### Admin

| Метод | Endpoint | Описание | Auth |
| :--- | :--- | :--- | :--- |
| GET | `/admin/*` | Админ-панель | Session Cookie |

---

## Для разработчиков

### Добавить новую миграцию

```bash
# 1. Измени модели в app/models/
# 2. Создай миграцию
docker-compose exec web flask db migrate -m "Описание изменений"

# 3. Проверь файл в migrations/versions/
# 4. Закоммить миграцию в Git
git add migrations/versions/xxxx_*.py
git commit -m "Add migration: описание"

# 5. Примени миграцию
docker-compose exec web flask db upgrade
```

### Проверить таблицы в БД

```bash
docker-compose exec db psql -U postgres -d hackathon_db -c "\dt"
```
---

## Технологии

| Компонент | Технология |
|-----------|------------|
| Backend | Python 3.11 + Flask |
| Database | PostgreSQL 15 |
| ORM | SQLAlchemy |
| Migrations | Alembic (Flask-Migrate) |
| Admin Panel | Flask-Admin + Flask-Login |
| API Auth | JWT (Flask-JWT-Extended) |
| Admin Auth | Session Cookie (Flask-Login) |
| Containerization | Docker + Docker Compose |