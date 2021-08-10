import os

from aiogram import Bot
from dotenv import load_dotenv

from app.text_parts import (PROVIDER_SELF, PROVIDER_TKB,
                            PROVIDER_FORTA_TECH, PROVIDER_BRS,
                            PROVIDER_WALLETTO)

load_dotenv()

TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN, parse_mode='HTML')

# Настройки webhook
WEBHOOK_IS_ACTIVE = (os.getenv('WEBHOOK_IS_ACTIVE', default=False).lower()
                     == 'true')
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH')
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# Настройки webserver
WEBAPP_HOST = os.getenv('WEBAPP_HOST')
WEBAPP_PORT = os.getenv('WEBAPP_PORT')

# Пользователи, которые могут использовать бота
accepted_user_id = list(map(int, os.getenv('ACCEPTED_USER_ID').split(',')))

# По каким чатам рассылать сообщение по выбранному провайдеру
chat_id = {
    PROVIDER_SELF: list(map(int, os.getenv('PROVIDER_SELF').split(','))),
    PROVIDER_TKB: list(map(int, os.getenv('PROVIDER_TKB').split(','))),
    PROVIDER_FORTA_TECH: list(map(int, os.getenv('PROVIDER_FORTA_TECH').split(','))),
    PROVIDER_BRS: list(map(int, os.getenv('PROVIDER_BRS').split(','))),
    PROVIDER_WALLETTO: list(map(int, os.getenv('PROVIDER_WALLETTO').split(',')))
}
