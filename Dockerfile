FROM python:3.11-slim

# Рабочая директория
WORKDIR /app

# Системные зависимости (для psycopg2 и curl в healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Настраиваем локаль для поддержки UTF-8
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV PYTHONIOENCODING=utf-8

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код проекта
COPY . .

# Создаём папку для логов
RUN mkdir -p /app/logs

# Переменные окружения
ENV FLASK_APP=app:create_app
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

# Открываем порт
EXPOSE 5000

# Health check для Docker
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/status || exit 1

# Команда запуска
CMD ["python", "manage.py"]