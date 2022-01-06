from aiogram import Dispatcher

from . import (start_notif, end_notif, edit_recipients_list,
               edit_providers_list, edit_white_list, errors,
               new_chat_event, delete_notif)


async def setup_all(dp: Dispatcher) -> None:
    """
    Init all setup-functions for registering in Dispatcher.
    """
    await start_notif.setup(dp)
    await end_notif.setup(dp)
    await edit_recipients_list.setup(dp)
    await edit_providers_list.setup(dp)
    await edit_white_list.setup(dp)
    await errors.setup(dp)
    await new_chat_event.setup(dp)
    await delete_notif.setup(dp)
