# Используем базовый образ Python
FROM python:3.11-alpine

# Установка переменных среды
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копирование зависимостей и установка зависимостей Python
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копирование кода бота в контейнер
COPY . /app/

# Команда для запуска бота
CMD ["main.py"]
