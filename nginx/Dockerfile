# Используем официальный образ Nginx
FROM nginx:latest

# Установка Certbot
RUN apt-get update && \
    apt-get install -y certbot python3-certbot-nginx

# Копирование конфигураций Nginx
COPY nginx.conf /etc/nginx/nginx.conf
COPY default.conf.template /etc/nginx/conf.d/default.conf.template

# Скрипт для старта Nginx и автоматической генерации сертификатов
COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

# Открытие портов
EXPOSE 80
EXPOSE 443

# Команда для старта Nginx и Certbot при запуске контейнера
CMD ["start.sh"]
