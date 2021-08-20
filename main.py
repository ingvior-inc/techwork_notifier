import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.executor import start_webhook

from app import handlers
from app.commands import set_commands
from app.settings import (WEBHOOK_IS_ACTIVE, WEBHOOK_URL, WEBHOOK_PATH,
                          WEBAPP_HOST, WEBAPP_PORT, TOKEN)


async def on_startup(dp: Dispatcher):
    logging.warning('Setting handlers...')
    handlers.setup_all(dp)
    logging.warning('Setting commands...')
    await set_commands(dp)
    if WEBHOOK_IS_ACTIVE:
        logging.warning('Setting webhook...')
        await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dp: Dispatcher):
    logging.warning('Shutting down..')

    await dp.storage.close()
    await dp.storage.wait_closed()

    await bot.delete_webhook()
    logging.warning('Webhook down')


if __name__ == '__main__':
    bot = Bot(token=TOKEN, parse_mode='HTML')
    dp = Dispatcher(bot, storage=MemoryStorage())
    try:
        if WEBHOOK_IS_ACTIVE:
            start_webhook(
                dispatcher=dp,
                webhook_path=WEBHOOK_PATH,
                on_startup=on_startup,
                on_shutdown=on_shutdown,
                skip_updates=True,
                host=WEBAPP_HOST,
                port=WEBAPP_PORT
            )
        else:
            executor.start_polling(dp, on_startup=on_startup,
                                   skip_updates=True)
    except Exception as E:
        logging.error(f'An error occurred while launching the bot - {E}')
