import logging
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(levelname)s | %(message)s',
                    datefmt='%d.%m.%Y, %H:%M:%S')

# Подключение к БД PostgreSQL
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

try:
    connect = psycopg2.connect(f"dbname={DB_NAME} "
                               f"user={DB_USER} "
                               f"password={DB_PASSWORD}")
    cur = connect.cursor()
    logging.warning('Database connection established!')
except Exception:
    logging.error('Database connection failed :(')


TOKEN = os.getenv('TOKEN')

# Настройки webhook
WEBHOOK_IS_ACTIVE = (os.getenv('WEBHOOK_IS_ACTIVE', default=False).lower()
                     == 'true')
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH')
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# Настройки webserver
WEBAPP_HOST = os.getenv('WEBAPP_HOST')
WEBAPP_PORT = os.getenv('WEBAPP_PORT')

# Список провайдеров
cur.execute('SELECT provider_desc FROM providers ORDER BY id')
providers = [i for sub in cur.fetchall() for i in sub]
