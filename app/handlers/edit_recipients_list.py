import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from app.const import Buttons, MessageParts
from app.general_functions import (white_list, get_providers_list,
                                   get_providers_chats_list,
                                   create_iter_keyboard,
                                   get_provider_id, get_chats_for_allocate,
                                   get_count_providers_with_chat)
from app.settings import cur, connect
from app.states import OrderEditingChats as States

buttons = (Buttons.ADD_CHAT, Buttons.DELETE_CHAT)


@white_list
async def check_providers_list(message: types.Message) -> None:
    parsed_list = {}
    for i in await get_providers_list():
        chats_list = await get_providers_chats_list(i, display_titles=True)
        parsed_list[i] = '\n'.join(chats_list)
    output_text = ''
    for provider, chats in parsed_list.items():
        output_text = output_text + f'<b>{provider}</b>:\n {chats}\n\n'

    await message.answer(f'{MessageParts.PROVIDERS_LIST}:\n\n'
                         f'{output_text}')


@white_list
async def start_editing_chats(message: types.Message) -> None:
    keyboard = await create_iter_keyboard(buttons)

    await States.waiting_for_situation.set()
    await message.answer(MessageParts.WAITING_FOR_SITUATION,
                         reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to '
                 f'{States.waiting_for_situation=}')


async def choice_of_situation(message: types.Message,
                              state: FSMContext) -> None:
    if message.text not in buttons:
        await message.answer(MessageParts.USE_KEYBOARD_PLEASE)
        return

    await state.update_data(chosen_situation=message.text)

    keyboard = await create_iter_keyboard(await get_providers_list(
        with_default=False))

    await States.waiting_for_provider.set()
    await message.answer(MessageParts.WAITING_FOR_PROVIDER,
                         reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to '
                 f'{States.waiting_for_provider=}')


async def choice_of_provider(message: types.Message,
                             state: FSMContext) -> None:
    if message.text not in await get_providers_list(with_default=False):
        await message.answer(MessageParts.USE_KEYBOARD_PLEASE)
        return

    await state.update_data(chosen_provider=message.text)

    user_data = await state.get_data()
    chosen_situation = user_data.get('chosen_situation')
    chosen_provider = user_data.get('chosen_provider')

    if chosen_situation == Buttons.ADD_CHAT:
        keyboard = await create_iter_keyboard(
            await get_chats_for_allocate())
    else:
        keyboard = await create_iter_keyboard(
            await get_providers_chats_list(chosen_provider,
                                           display_titles=True))

    await States.waiting_for_chat_id.set()
    await message.answer(MessageParts.WAITING_FOR_CHAT_ID,
                         reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to '
                 f'{States.waiting_for_chat_id=}')


async def choice_of_chat_id(message: types.Message, state: FSMContext) -> None:

    if message.text not in await get_chats_for_allocate():
        await message.answer(MessageParts.USE_KEYBOARD_PLEASE)
        return

    await state.update_data(chosen_chat=message.text.split()[0])

    user_data = await state.get_data()
    chosen_situation = user_data.get('chosen_situation')
    chosen_chat = user_data.get('chosen_chat')
    chosen_provider = user_data.get('chosen_provider')

    provider_id = await get_provider_id(chosen_provider)

    if chosen_situation == Buttons.ADD_CHAT:
        cur.execute(f"INSERT INTO chats(chat_id, provider_id) "
                    f"VALUES({chosen_chat}, {provider_id}) "
                    f"ON CONFLICT DO NOTHING ")
        cur.execute(f"INSERT INTO chats(chat_id, provider_id) "
                    f"VALUES({chosen_chat}, {1}) "
                    f"ON CONFLICT DO NOTHING ")
        await message.answer(MessageParts.CHAT_WAS_ADDED)
        logging.info(f'{message.chat.username}({message.chat.id}) '
                     f'was add chat {chosen_chat} '
                     f'to provider {chosen_provider}')

    elif chosen_situation == Buttons.DELETE_CHAT:
        cur.execute(f"DELETE FROM chats "
                    f"WHERE chat_id = {chosen_chat} "
                    f"AND provider_id = {provider_id}")

        if await get_count_providers_with_chat(chosen_chat) <= 1:
            cur.execute(f"DELETE FROM chats "
                        f"WHERE chat_id = {chosen_chat} "
                        f"AND provider_id = {1}")

        await message.answer(MessageParts.CHAT_WAS_DELETED,
                             reply_markup=await create_iter_keyboard(
                                 await get_providers_chats_list(
                                     chosen_provider, display_titles=True)))
        logging.info(f'{message.chat.username}({message.chat.id}) '
                     f'was delete chat {chosen_chat} '
                     f'from provider {chosen_provider}')

    connect.commit()


async def setup(dp: Dispatcher) -> None:
    """
    Registering handlers in Dispatcher.
    """
    dp.register_message_handler(check_providers_list,
                                commands='check_recipients',
                                state=None)
    dp.register_message_handler(start_editing_chats,
                                commands='edit_recipients',
                                state=None)
    dp.register_message_handler(choice_of_situation,
                                state=States.waiting_for_situation)
    dp.register_message_handler(choice_of_provider,
                                state=States.waiting_for_provider)
    dp.register_message_handler(choice_of_chat_id,
                                state=States.waiting_for_chat_id)
