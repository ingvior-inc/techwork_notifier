import logging
from asyncio import sleep

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import ChatNotFound, ChatIdIsEmpty, BotKicked

from app.const import Situations, Buttons, MessageParts
from app.general_functions import (white_list, get_current_time,
                                   get_providers_list, create_iter_keyboard,
                                   convert_to_hashtag, get_provider_id,
                                   get_providers_chats_list)
from app.settings import cur, connect
from app.states import OrderBuildingNotif as States
from .delete_notif import last_messages


async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    """
    Exit work in any intermediate State.
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'cancelling state {current_state}')

    await state.finish()

    await message.reply(MessageParts.AFTER_CANCEL_CURRENT_OPERATION,
                        reply_markup=types.ReplyKeyboardRemove())


async def create_incident(provider: str) -> int:
    """
    Creates a new incident in active_incidents table and returns its id.
    """
    provider_id = await get_provider_id(provider)
    cur.execute(f"INSERT INTO active_incidents (provider_id) "
                f"VALUES ({provider_id}) RETURNING id")
    new_incident_id = cur.fetchone()[0]
    logging.warning(f'Incident was created - {new_incident_id}')
    return new_incident_id


async def send_notifications(message: types.Message,
                             provider: str,
                             text: str,
                             incident_id: int = None) -> None:
    """
    Sending messages based on selected provider.
    """
    chats_recipients = []
    last_messages.clear()

    for i in await get_providers_chats_list(provider):
        try:
            sended = await message.bot.send_message(chat_id=i,
                                                    text=text)
            chats_recipients.append(sended.chat.title)

            logging.warning(f'{send_notifications=} Message sent to '
                            f'"{sended.chat.title}" ({sended.chat.id})')

            if incident_id:
                cur.execute(f"INSERT INTO "
                            f"incidents_chats_messages (message_id, "
                            f"chat_id, incident_id) "
                            f"VALUES ({sended.message_id}, {i}, "
                            f"{incident_id})")

            last_messages[i] = sended.message_id

        except (ChatNotFound, ChatIdIsEmpty) as E:
            await message.answer(f'ID {i}: чат не найден')
            logging.error(f'ID {i} - {E}')
        except BotKicked as E:
            await message.answer(f'ID {i}: бот удалён из чата')
            logging.error(f'ID {i} - {E}')

        await sleep(0.1)

    if chats_recipients:
        connect.commit()
        await message.answer(f'Текст отправлен в чаты:\n\n'
                             f'{chats_recipients}\n\n'
                             f'Содержание:\n\n{text}',
                             reply_markup=types.ReplyKeyboardRemove())
        return

    logging.error(f'{send_notifications=} sending failed')
    await message.answer(MessageParts.SENDING_FAILED,
                         reply_markup=types.ReplyKeyboardRemove())


@white_list
async def start_building_notif(message: types.Message) -> None:
    keyboard = await create_iter_keyboard(Situations.LIST)

    await States.waiting_for_situation.set()
    await message.answer(MessageParts.WAITING_FOR_SITUATION,
                         reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to {States.waiting_for_situation=}')


async def choice_of_situation(message: types.Message,
                              state: FSMContext) -> None:
    if message.text not in Situations.LIST:
        await message.answer(MessageParts.USE_KEYBOARD_PLEASE)
        return

    await state.update_data(chosen_situation=message.text)

    keyboard = await create_iter_keyboard(await get_providers_list())

    await States.next()
    await message.answer(MessageParts.WAITING_FOR_PROVIDER,
                         reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to {States.waiting_for_provider=}')


async def choice_of_provider(message: types.Message,
                             state: FSMContext) -> None:
    if message.text not in await get_providers_list():
        await message.answer(MessageParts.USE_KEYBOARD_PLEASE)
        return

    await state.update_data(chosen_provider=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(Buttons.NOW)
    keyboard.add(Buttons.CANCEL)

    await States.next()
    await message.answer(MessageParts.WAITING_FOR_WRITING_DATE_AND_TIME,
                         reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to {States.waiting_for_date_and_time=}')


async def writing_date_and_time(message: types.Message,
                                state: FSMContext) -> None:
    if message.text == Buttons.NOW:
        time_now = await get_current_time(delta=3)
        await state.update_data(written_date_and_time=(f'{Buttons.NOW} '
                                                       f'({time_now} МСК)'))
    else:
        await state.update_data(written_date_and_time=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(Buttons.CANCEL)

    await States.next()
    await message.answer(MessageParts.WAITING_FOR_WRITING_DESCRIPTION,
                         reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to {States.waiting_for_description=}')


async def writing_description(message: types.Message,
                              state: FSMContext) -> None:
    await state.update_data(written_description=message.text)

    user_data = await state.get_data()
    chosen_provider = user_data.get('chosen_provider')
    chosen_situation = user_data.get('chosen_situation')
    situation_hashtag = await convert_to_hashtag(chosen_situation)
    provider_hashtag = await convert_to_hashtag(chosen_provider)

    incident_id = None
    if chosen_situation == Situations.TECHNICAL_FAILURE:
        incident_id = await create_incident(chosen_provider)

    final_text = (f"<em>{situation_hashtag}</em>\n"
                  f"<b>{MessageParts.PROVIDER}:</b> {provider_hashtag}\n"
                  f"<b>{MessageParts.WHEN}:</b> "
                  f"{user_data.get('written_date_and_time')}\n\n"
                  f"{user_data.get('written_description')}")

    await send_notifications(message, chosen_provider, final_text, incident_id)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'finished scenario "start_notif"')

    await state.finish()


async def setup(dp: Dispatcher) -> None:
    """
    Registering handlers in Dispatcher.
    """
    dp.register_message_handler(cancel_handler, commands='cancel', state='*')
    dp.register_message_handler(cancel_handler,
                                Text(equals=Buttons.CANCEL, ignore_case=True),
                                state='*')
    dp.register_message_handler(start_building_notif,
                                commands='start', state=None)
    dp.register_message_handler(choice_of_situation,
                                state=States.waiting_for_situation)
    dp.register_message_handler(choice_of_provider,
                                state=States.waiting_for_provider)
    dp.register_message_handler(writing_date_and_time,
                                state=States.waiting_for_date_and_time)
    dp.register_message_handler(writing_description,
                                state=States.waiting_for_description)
