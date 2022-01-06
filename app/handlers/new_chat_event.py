import logging

from aiogram import types, Dispatcher

from app.settings import cur, connect
from app.general_functions import get_admins_list
from app.const import MessageParts


async def add_chat(message: types.Message) -> None:
    if message.chat.id < 0:
        text = (f'{MessageParts.NEW_CHAT_DETECTED}:\n'
                f'«{message.chat.title}» ({message.chat.id})')
        cur.execute(f"INSERT INTO chats_for_allocate(chat_id, chat_title) "
                    f"VALUES "
                    f"({message.chat.id}, '{message.chat.title}') "
                    f"ON CONFLICT DO NOTHING ")
        connect.commit()
        await message.bot.send_message(chat_id=message.from_user.id,
                                       text=text)


async def new_chat_found(chat_member: types.chat_member) -> None:
    if chat_member.from_user.id in await get_admins_list():
        if chat_member.new_chat_member.status == 'member':
            text = (f'{MessageParts.NEW_CHAT_DETECTED}:\n'
                    f'«{chat_member.chat.title}» ({chat_member.chat.id})')
            cur.execute(f"INSERT INTO chats_for_allocate(chat_id, chat_title) "
                        f"VALUES "
                        f"({chat_member.chat.id}, '{chat_member.chat.title}') "
                        f"ON CONFLICT DO NOTHING ")
            logging.info(f'Bot was added to «{chat_member.chat.title}»'
                         f'({chat_member.chat.id})')
        elif chat_member.new_chat_member.status == 'left':
            text = (f'{MessageParts.BOT_WAS_DELETED}:\n'
                    f'«{chat_member.chat.title}» ({chat_member.chat.id})')
            cur.execute(f"DELETE FROM chats_for_allocate "
                        f"WHERE chat_id = {chat_member.chat.id}")
            logging.info(f'Bot was deleted from «{chat_member.chat.title}»'
                         f'({chat_member.chat.id})')
        else:
            logging.error(f'{new_chat_found=}: failed to parse bot status')
            return

        connect.commit()
        await chat_member.bot.send_message(chat_id=chat_member.from_user.id,
                                           text=text)


async def setup(dp: Dispatcher) -> None:
    """
    Registering handlers in Dispatcher.
    """
    dp.register_message_handler(add_chat, commands='add_chat')
    dp.register_my_chat_member_handler(new_chat_found)
