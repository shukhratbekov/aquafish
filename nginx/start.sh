#!/bin/bash

# Запуск Certbot для генерации SSL сертификатов
certbot --nginx --non-interactive --agree-tos --email shukhratbekovb@gmail.com -d shukhratbekov.uz -d bot.shukhratbekov.uz

# Запуск Nginx
nginx -g "daemon off;"
