import logging
import os
import sys

import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Настройки логгирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(levelname)s | %(message)s',
                    datefmt='%d.%m.%Y, %H:%M:%S')

# Подключение к БД PostgreSQL
try:
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', default='db')
    POSTGRES_DB = os.getenv('POSTGRES_DB', default='postgres')
    POSTGRES_USER = os.getenv('POSTGRES_USER', default='postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', default='111111wwwww')
    connect = psycopg2.connect(host=POSTGRES_HOST,
                               dbname=POSTGRES_DB,
                               user=POSTGRES_USER,
                               password=POSTGRES_PASSWORD)
    cur = connect.cursor()
    logging.warning('Database connection established!')
except Exception as e:
    logging.error(f'Database connection failed - {e}')
    sys.exit(1)

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
