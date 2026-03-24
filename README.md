# mini_t1

Система оценки хакатонов. Backend на Flask + PostgreSQL.

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

Сервер доступен: `http://127.0.0.1:5000`

### 3. Примени миграции

```bash
docker-compose exec web flask db upgrade
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
| `docker-compose up --build` | Собрать и запустить проект |
| `docker-compose down` | Остановить контейнеры |
| `docker-compose down -v` | Остановить + удалить базу данных |
| `flask db migrate -m "Описание"` | Создать новую миграцию |
| `flask db upgrade` | Применить миграции |
| `flask db downgrade` | Откатить миграцию |
| `flask create-superuser` | Создать суперпользователя для админки |

---

## API Endpoints

| Метод | Endpoint | Описание |
| :--- | :--- | :--- |
| POST | `/api/auth/register` | Регистрация пользователя |
| POST | `/api/auth/login` | Вход (получение JWT токена) |
| POST | `/api/auth/logout` | Выход (инвалидация токена) |
| GET | `/admin/*` | Админ-панель (требуется Session Cookie) |
| GET | `/api/auth/me` | Получить текущего пользователя | JWT |

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