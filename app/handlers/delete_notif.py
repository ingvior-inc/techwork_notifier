import logging
from asyncio import sleep

from aiogram import types, Dispatcher

from app.const import MessageParts
from app.general_functions import white_list


last_messages = {}


@white_list
async def delete_last_messages(message: types.Message) -> None:
    if not last_messages:
        await message.answer(MessageParts.NO_LAST_MESSAGES)
        logging.error(f'{message.chat.username}({message.chat.id}) '
                      f'last messages does not exist')
        return
    for i, j in last_messages.items():
        await message.bot.delete_message(chat_id=i, message_id=j)
        logging.warning(f'{delete_last_messages=} '
                        f'Message deleted {i} / {j}')
        await sleep(0.1)
    last_messages.clear()
    await message.answer(MessageParts.LAST_MESSAGES_DELETED)


async def setup(dp: Dispatcher):
    """
    Registering handlers in Dispatcher.
    """
    dp.register_message_handler(delete_last_messages,
                                commands='del', state=None)
