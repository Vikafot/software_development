import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv('DB_NAME')
SUPER_USER = os.getenv('SUPER_DB_USER', 'postgres')
SUPER_PASS = os.getenv('SUPER_DB_PASS', '')
HOST = os.getenv('DB_HOST', 'localhost')

def create_database():
    conn = psycopg2.connect(dbname="postgres", user=SUPER_USER, password=SUPER_PASS, host=HOST)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (DB_NAME,))
    if not cur.fetchone():
        cur.execute(f"CREATE DATABASE {DB_NAME};")
        print(f"БД '{DB_NAME}' создана")
    else:
        print(f"БД '{DB_NAME}' уже существует")
    cur.close()
    conn.close()

def create_tables():
    from app import create_app
    from db import db
    
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Таблицы инициализированы")

if __name__ == '__main__':
    create_database()
    create_tables()
