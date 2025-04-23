# Используем официальный образ Node.js LTS (с длинным сроком поддержки)
FROM node:lts AS build-stage

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копируем зависимости
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем исходный код приложения
COPY . .

# Собираем приложение для production с минификацией
RUN npm run build

# Второй этап Dockerfile - настройка Nginx для сервера статики
FROM nginx:stable-alpine

# Копируем наш пользовательский nginx.conf в контейнер
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копируем сборку Vue.js из предыдущего этапа в рабочую директорию Nginx
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Конфигурируем Nginx (можно также добавить свой nginx.conf)
EXPOSE 80

# Команда для запуска Nginx внутри контейнера
CMD ["nginx", "-g", "daemon off;"]
