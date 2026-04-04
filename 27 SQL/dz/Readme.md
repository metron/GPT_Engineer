# Выполнение ДЗ, пример использования связки Python, PostgreeSQL, sqlalchemy
## Установка python3.11 и библиотек
python3.11 -m venv .venv
pip install --upgrade pip
pip install psycopg2 sqlalchemy pandas

## Установка БД
sudo apt install postgresql
sudo systemctl disable postgresql.service 
### Узнать версию PostgreeSQL
psql --version
### Настраиваем пользователя postgres
#### Задаём пароль
sudo -u postgres psql
ALTER USER postgres WITH PASSWORD '1';
sudo vim /var/lib/postgresql/.psql_history
#### Настраиваем права доступа сервиса приложения PgSQL
##### Редактируем файл настроек
sudo vim /etc/postgresql/16/main/pg_hba.conf
##### Находим там строку
local  all  postgres  peer
##### Заменяем на
local  all  postgres  md5
##### Перезапускаем сервис
sudo systemctl restart postgresql.service
##### Можно входить по команде ниже, указав пароль
psql -U postgres -W

### Устанавливаем psycopg2, предварительно установив зависимости
sudo apt install libpq-dev python3.11-dev gcc
pip install psycopg2


