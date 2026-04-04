import pandas as pd
from sqlalchemy import (Column, Integer, MetaData, Numeric, Table, Text,
                        create_engine, insert)

from db_exist import make_sure_db_exists
from env import pg_password, pg_user

pg_db_name = "27dz"
# Использование
make_sure_db_exists(pg_db_name, pg_user, pg_password)
engine = create_engine(f"postgresql+psycopg2://{pg_user}:{pg_password}@localhost/{pg_db_name}")
engine.connect()

metadata = MetaData()
apartments = Table(
    "apartments",
    metadata,
    Column("id", Integer(), primary_key=True),
    Column("city", Text(), nullable=True),
    Column("district", Text(), nullable=True),
    Column("address", Text(), nullable=True),
    Column("area", Numeric(), nullable=True),
    Column("rooms", Integer(), nullable=True),
    Column("floor", Integer(), nullable=True),
    Column("year_built", Integer(), nullable=True),
    Column("price", Numeric(), nullable=True),
    Column("type", Text(), nullable=True)
)
metadata.create_all(engine)

# 3. Добавляем данные
fields = 'city', 'district', "address", "area", "rooms", "floor", "year_built", "price", "type"
with engine.connect() as conn:
    # Вставка нескольких записей (массовая вставка)
    conn.execute(insert(apartments), [
        dict(zip(fields, ["Москва", "Обручевский", "Волгина 2", 30.4, 1, 27, 2024, 20300000, "Новостройка"])),
        dict(zip(fields, ["Москва", "Зюзино", "Зюзино 2", 61.4, 3, 7, 2020, 22300000, "Вторичка"])),
        dict(zip(fields, ["Москва", "Чертаново", "Чертановская", 130.4, 4, 17, 2014, 40300000, "Вторичка"])),
        dict(zip(fields, ["Сталинград", "Сталинский", "Сталина 17", 230.4, 10, 7, 2026, 120300000, "Новостройка"])),
        dict(zip(fields, ["Сталинград", "Кировский", "Кирова 12", 70.4, 3, 2, 2025, 19200000, "Новостройка"])),
        dict(zip(fields, ["Питер", "Обручевский", "Волгина 2", 30.4, 1, 27, 2024, 3000000, "Новостройка"])),
        dict(zip(fields, ["Севастополь", "Обручевский", "Волгина 2", 30.4, 1, 27, 2024, 4000000, "Новостройка"])),
        dict(zip(fields, ["Петропавловск Камчатский", "Обручевский", "Волгина 2", 30.4, 1, 27, 2024, 2000000, "Новостройка"])),
        dict(zip(fields, ["Саратов", "Обручевский", "Волгина 2", 30.4, 1, 27, 2024, 4500000, "Новостройка"])),
        dict(zip(fields, ["Калининград", "Обручевский", "Волгина 2", 30.4, 1, 27, 2024, 5000000, "Новостройка"])),
    ])
    conn.commit()

with engine.connect() as conn:
    df = pd.read_sql("SELECT * FROM apartments WHERE price < 5000000", conn)
print(df)
