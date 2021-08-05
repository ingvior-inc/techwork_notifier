import os

from aiogram import Bot
from dotenv import load_dotenv

from app.text_parts import (PROVIDER_SELF, PROVIDER_TKB,
                            PROVIDER_FORTA_TECH, PROVIDER_BRS)

load_dotenv()

TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN, parse_mode='HTML')

# Настройки webhook
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH')
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# Настройки webserver
WEBAPP_HOST = os.getenv('WEBAPP_HOST')
WEBAPP_PORT = os.getenv('WEBAPP_PORT')

# Пользователи, которые могут использовать бота
accepted_user_id = (512309881, 170476466)

# По каким чатам рассылать сообщение по выбранному провайдеру
chat_id = {
    PROVIDER_SELF: (-529458513, -477364969, -579903648, -535541196,
                    -592277061),
    PROVIDER_TKB: (-529458513, -592277061),
    PROVIDER_FORTA_TECH: (-477364969, -579903648, -535541196),
    PROVIDER_BRS: (-529458513, )
}
