import logging
import os

import psycopg2
from dotenv import load_dotenv
from . import create_db_sceleton

load_dotenv()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(levelname)s | %(message)s',
                    datefmt='%d.%m.%Y, %H:%M:%S')

# Подключение к БД PostgreSQL
try:
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    connect = psycopg2.connect(dbname=DB_NAME,
                               user=DB_USER,
                               password=DB_PASSWORD)
    cur = connect.cursor()
    create_db_sceleton.create_tables(connect, cur)
    logging.warning('Database connection established!')
# Если хостинг - Heroku
except psycopg2.OperationalError:
    DATABASE_URL = os.environ.get('DATABASE_URL')
    connect = psycopg2.connect(DATABASE_URL)
    cur = connect.cursor()
    create_db_sceleton.create_tables(connect, cur)
    logging.warning('Database connection established!')

# Токен бота
TOKEN = os.getenv('TOKEN')

# Настройки webhook
WEBHOOK_IS_ACTIVE = (os.getenv('WEBHOOK_IS_ACTIVE', default='False').lower()
                     == 'true')
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH')
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# Настройки webserver
WEBAPP_HOST = os.getenv('WEBAPP_HOST')
WEBAPP_PORT = os.getenv('WEBAPP_PORT')
