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

## 📋 Основные команды

| Команда | Описание |
| :--- | :--- |
| `docker-compose up --build` | Собрать и запустить проект |
| `docker-compose down` | Остановить контейнеры |
| `docker-compose down -v` | Остановить + удалить базу данных |
| `flask db migrate -m "Описание"` | Создать новую миграцию |
| `flask db upgrade` | Применить миграции |
| `flask db downgrade` | Откатить миграцию |

---

## 📡 API Endpoints

| Метод | Endpoint | Описание |
| :--- | :--- | :--- |
| GET | `/api/hello` | Проверка работы API |

---

## 🔧 Для разработчиков

### Добавить новую миграцию

```bash
# 1. Измени модели в app/models.py
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
