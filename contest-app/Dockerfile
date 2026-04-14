
FROM node:22-alpine


WORKDIR /app

# Копируем package файлы для кэширования зависимостей
COPY package*.json ./

# Устанавливаем зависимости (включая @angular/cli)
RUN npm ci

# Копируем исходный код
COPY . .

# Открываем порт для dev-сервера
EXPOSE 4200


# Запускаем dev-сервер с proxy для API
CMD ["npx", "ng", "serve", "--host", "0.0.0.0", "--port", "4200", "--poll", "2000", "--proxy-config", "proxy.conf.json"]

