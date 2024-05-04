# Используем базовый образ Python
FROM python:3.11-alpine

# Установка переменных среды
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Создаем директорию для кода приложения внутри контейнера
RUN mkdir /app

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем все файлы из текущей директории в контейнер
COPY . /app/

# Собираем статические файлы Django
RUN python manage.py collectstatic --noinput
RUN python manage.py makemigrations --noinput
RUN python manage.py migrate --noinput

# Запускаем Gunicorn для приложения Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
