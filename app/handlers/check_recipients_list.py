from pprint import pformat

from aiogram import types, Dispatcher

from app.functions import white_list
from app.settings import cur, providers


@white_list
async def check_providers_list(message: types.Message):
    parsed_list = {}
    for i in providers:
        cur.execute(f"SELECT chat_id "
                    f"FROM providers "
                    f"JOIN chats ON providers.id = chats.provider_id "
                    f"WHERE providers.provider_desc = '{i}'")
        parsed_list[i] = [i for sub in cur.fetchall() for i in sub]
    parsed_list = pformat(parsed_list)
    await message.answer(f'Список провайдеров: \n\n'
                         f'{parsed_list}')


def setup(dp: Dispatcher):
    """
    Регистрация хандлеров в диспетчере
    """
    dp.register_message_handler(check_providers_list,
                                commands='check_list',
                                state=None)
