import logging
import socket

from aiogram.utils.executor import start_webhook

from app.handlers import dp
from app.settings import (bot, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST,
                          WEBAPP_PORT)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(levelname)s — %(message)s',
                    datefmt='%d.%m.%Y, %H:%M:%S',)


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    await bot.delete_webhook()

    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Webhook down!')


if __name__ == '__main__':
    try:
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT
        )
    except socket.gaierror:
        logging.error('Failed to connect to webserver host')
    except Exception as E:
        logging.error(f'An error occurred while connecting - {E}')
