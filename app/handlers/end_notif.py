import logging
from asyncio import sleep

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BadRequest

from app.const import MessageParts
from app.general_functions import (white_list, create_iter_keyboard,
                                   get_active_incidents_list,
                                   get_incidents_chats_messages_id)
from app.settings import cur, connect
from app.states import OrderEndingNotif as States


async def send_end_notifications(message: types.Message,
                                 incident_id: int,
                                 text: str) -> None:
    """
    Sending messages about end of the incident.
    """
    for i, j in await get_incidents_chats_messages_id(incident_id=incident_id):
        try:
            await message.bot.send_message(chat_id=i, reply_to_message_id=j,
                                           text=text)
            logging.warning(f'{send_end_notifications=} Message '
                            f'sent {i} / {j}')

        except BadRequest:
            logging.error(f'{send_end_notifications=} Chat {i} / Message {j} '
                          f'does not exist')
            await message.answer(f'Связки чат {i} / сообщение {j} '
                                 f'не существует')

        await sleep(0.1)

    cur.execute(f"DELETE FROM active_incidents WHERE id = {incident_id}")
    connect.commit()

    await message.answer(MessageParts.INCIDENT_ENDED,
                         reply_markup=types.ReplyKeyboardRemove())


@white_list
async def start_ending_notif(message: types.Message) -> None:
    if not await get_active_incidents_list():
        await message.answer(MessageParts.NO_ACTIVE_INCIDENTS)
        return

    keyboard = await create_iter_keyboard(await get_active_incidents_list(
        display_details=True))

    await States.waiting_for_incident.set()
    await message.answer(MessageParts.WHICH_INCIDENT_NEED_END,
                         reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to {States.waiting_for_incident=}')


async def choice_of_incident(message: types.Message,
                             state: FSMContext) -> None:
    if message.text not in await get_active_incidents_list(
            display_details=True):
        await message.answer(MessageParts.USE_KEYBOARD_PLEASE)
        return

    await state.update_data(chosen_incident=message.text.split()[0])

    user_data = await state.get_data()
    chosen_incident = user_data.get('chosen_incident')

    final_text = MessageParts.INCIDENT_ENDED

    await send_end_notifications(message, chosen_incident, final_text)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'finished scenario "end_notif"')

    await state.finish()


async def setup(dp: Dispatcher) -> None:
    """
    Registering handlers in Dispatcher.
    """
    dp.register_message_handler(start_ending_notif,
                                commands='end', state=None)
    dp.register_message_handler(choice_of_incident,
                                state=States.waiting_for_incident)
