import logging

from aiogram import executor

from app.handlers import dp

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(levelname)s — %(message)s',
                    datefmt='%d.%m.%Y, %H:%M:%S',)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
