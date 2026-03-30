# windows
python -m venv .venv
source ./.venv/Script/activate

# Linux / MacOs
python3 -m venv .venv
source ./.venv/bin/activate

# Деактивировать виртуальное окружение
deactivate

# Установка django
pip install django

# Посмотреть установленные пакеты
pip list

# Создание django проекта
django-admin startproject config .

# Создание приложения
python manage.py startapp assistant_app

# Установка пакетов для RAG
pip install -U langchain langchain-community langchain-openai faiss-cpu langchain-text-splitters

# Установка пакета для работы с переменными окружения
pip install python-dotenv

# Установка пакета для HTTP-запросов
pip install requests

# Применить миграции
python manage.py migrate