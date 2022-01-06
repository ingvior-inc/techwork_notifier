import datetime
import logging
import typing

from aiogram import types

from app.const import Buttons, MessageParts
from app.settings import cur


def white_list(func):
    """
    Bot can be used only by admins.
    """
    async def wrapper(message: types.Message):
        if message.chat.id in await get_admins_list():
            logging.warning(f'{message.chat.username}({message.chat.id})'
                            f' - accepted')
            return await func(message)
        # Ignor calls to the bot from groups
        elif message.chat.id < 0:
            logging.warning(f'{message.chat.title}({message.chat.id}):'
                            f' - is group, ignored')
            return
        else:
            logging.warning(f'{message.chat.username}({message.chat.id})'
                            f' - denied')
            return await message.answer(MessageParts.ACCESS_DENIED)
    return wrapper


async def get_current_time(delta: int = 3) -> str:
    """
    Returns current time. Default - GMT+3 (Moscow).
    """
    delta = datetime.timedelta(hours=delta)
    now_utc = datetime.datetime.now(datetime.timezone.utc) + delta
    return now_utc.strftime('%d.%m.%Y, %H:%M')


async def get_providers_list(with_default: bool = True) -> list:
    """
    Returns a list of providers.
    with_default = False - all providers except provider with id 1.
    """
    if with_default:
        cur.execute('SELECT provider_desc '
                    'FROM providers '
                    'ORDER BY id')
    else:
        cur.execute('SELECT provider_desc '
                    'FROM providers '
                    'WHERE id != 1 '
                    'ORDER BY id')
    return [i for sub in cur.fetchall() for i in sub]


async def get_admins_list() -> list:
    """
    Returns a list of admins who can use bot.
    """
    cur.execute('SELECT chat_id FROM white_list')
    return [i for sub in cur.fetchall() for i in sub]


async def get_chats_for_allocate() -> list:
    """
    Returns a list of chats available to allocate.
    """
    cur.execute(f'SELECT chats_for_allocate.chat_id, chat_title '
                f'FROM chats_for_allocate')
    return [f'{i} | {j}' for i, j in cur.fetchall()]


async def get_providers_chats_list(provider: str,
                                   display_titles: bool = False) -> \
        typing.Union[list, str]:
    """
    Returns a list of chats by provider name.
    display_titles = True - returns a formated list along with chat names.
    """
    if display_titles:
        cur.execute(f"SELECT chats.chat_id, chats_for_allocate.chat_title "
                    f"FROM chats "
                    f"JOIN chats_for_allocate ON "
                    f"chats.chat_id = chats_for_allocate.chat_id "
                    f"JOIN providers ON chats.provider_id = providers.id "
                    f"WHERE providers.provider_desc = '{provider}'")
        return [f'{i} | {j}' for i, j in cur.fetchall()]

    cur.execute(f"SELECT chat_id "
                f"FROM chats "
                f"JOIN providers ON chats.provider_id = providers.id "
                f"WHERE providers.provider_desc = '{provider}'")
    return [i for sub in cur.fetchall() for i in sub]


async def get_active_incidents_list(display_details: bool = False) -> list:
    """
    Returns a list with id of active incidents.
    display_details = True -
    returns a list in format: Incident | Provider | Situation type.
    """
    if display_details:
        cur.execute('SELECT active_incidents.id, provider_desc, created_at '
                    'FROM active_incidents '
                    'JOIN providers '
                    'ON active_incidents.provider_id = providers.id ')
        return [f"{i} | {j} | {k.strftime('%d-%m-%Y | %H:%M')}"
                for i, j, k in cur.fetchall()]

    cur.execute('SELECT active_incidents.id FROM active_incidents')
    return [str(i) for sub in cur.fetchall() for i in sub]


async def get_incidents_chats_messages_id(incident_id: int) -> list:
    """
    Returns a list of chat id / message id related by current incident id.
    """
    cur.execute(f"SELECT chat_id, message_id "
                f"FROM incidents_chats_messages "
                f"WHERE incident_id = {incident_id}")
    return [i for i in cur.fetchall()]


async def get_provider_id(provider: str) -> int:
    """
    Returns provider id by his name.
    """
    cur.execute(f"SELECT id "
                f"FROM providers "
                f"WHERE provider_desc = '{provider}'")
    return cur.fetchone()[0]


async def get_count_providers_with_chat(chat_id: int) -> int:
    """
    Returns a count of providers linked with current chat id.
    """
    cur.execute(f'SELECT COUNT(chat_id) '
                f'FROM chats '
                f'WHERE '
                f'chat_id = {chat_id}')
    return cur.fetchone()[0]


async def create_iter_keyboard(
        iterable: typing.Iterable) -> types.ReplyKeyboardMarkup:
    """
    Returns a Telegram keyboard object with buttons based on inputed
    iterable object.
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in iterable:
        keyboard.add(i)
    keyboard.add(Buttons.CANCEL)
    return keyboard


async def convert_to_hashtag(name: str) -> str:
    """
    Returns goted string as a hashtaged string.
    """
    if name[0] != '#':
        return '#' + name.replace(' ', '_')
