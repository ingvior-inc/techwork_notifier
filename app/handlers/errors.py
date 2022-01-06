import logging

import psycopg2
from aiogram import types, Dispatcher

from app.settings import cur


async def postgres_integrity_errors(update: types.Update,
                                    exception: Exception) -> bool:
    logging.error(exception)
    cur.execute('ROLLBACK')
    return True


async def setup(dp: Dispatcher):
    """
    Registering handlers in Dispatcher.
    """
    dp.register_errors_handler(postgres_integrity_errors,
                               exception=psycopg2.IntegrityError)
