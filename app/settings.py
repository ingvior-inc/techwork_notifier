import os

from aiogram import Bot
from dotenv import load_dotenv

from app.text_parts import (PROVIDER_SELF, PROVIDER_TKB,
                            PROVIDER_FORTA_TECH, PROVIDER_BRS)

load_dotenv()

TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN, parse_mode='HTML')

# Пользователи, которые могут использовать бота
accepted_user_ids = (512309881, 170476466)

# По каким чатам рассылать сообщение по выбранному провайдеру
chat_ids = {
    PROVIDER_SELF: [-520470585, -599355925, -550816100],
    PROVIDER_TKB: [-520470585],
    PROVIDER_FORTA_TECH: [-599355925],
    PROVIDER_BRS: [-550816100]
}
