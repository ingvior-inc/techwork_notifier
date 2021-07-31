import os

from dotenv import load_dotenv

from aiogram import Bot

from app.message_parts import (PROVIDER_SELF, PROVIDER_TKB,
                               PROVIDER_FORTA_TECH, PROVIDER_BRS)

load_dotenv()

TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN, parse_mode='HTML')

CHAT_ID = {
    PROVIDER_SELF: [-520470585, -599355925],
    PROVIDER_TKB: [-520470585],
    PROVIDER_FORTA_TECH: [-599355925],
    PROVIDER_BRS: []
}
