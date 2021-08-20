import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from app.const import (BUTTON_CANCEL, USE_KEYBOARD_PLEASE,
                       ADD_CHAT, DELETE_CHAT, ADD_PROVIDER, DELETE_PROVIDER)
from app.functions import white_list
from app.settings import providers, cur, connect
from app.states import OrderEditingChatsOrProviders


situations = [ADD_CHAT, DELETE_CHAT, ADD_PROVIDER, DELETE_PROVIDER]


@white_list
async def start_editing_chats_or_providers(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in situations:
        keyboard.add(i)
    keyboard.add(BUTTON_CANCEL)

    await OrderEditingChatsOrProviders.waiting_for_situation.set()
    await message.answer('Что хотим сделать?', reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to '
                 f'{OrderEditingChatsOrProviders.waiting_for_situation}')


async def choice_of_situation(message: types.Message, state: FSMContext):
    if message.text not in situations:
        await message.answer(USE_KEYBOARD_PLEASE)
        return

    await state.update_data(chosen_situation=message.text)
    user_data = await state.get_data()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if user_data.get('chosen_situation') in (ADD_CHAT, DELETE_CHAT):
        for i in providers:
            keyboard.add(i)
        keyboard.add(BUTTON_CANCEL)

        await OrderEditingChatsOrProviders.waiting_for_provider.set()
        await message.answer('Для какого провайдера?',
                             reply_markup=keyboard)

        logging.info(f'{message.chat.username}({message.chat.id}) '
                     f'switched to '
                     f'{OrderEditingChatsOrProviders.waiting_for_provider}')
        return

    keyboard.add(BUTTON_CANCEL)

    await OrderEditingChatsOrProviders.waiting_for_write_provider.set()
    await message.answer('Напишите имя нового провайдера',
                         reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to '
                 f'{OrderEditingChatsOrProviders.waiting_for_write_provider}')


async def choice_of_provider(message: types.Message, state: FSMContext):
    if message.text not in providers:
        await message.answer(USE_KEYBOARD_PLEASE)
        return

    await state.update_data(chosen_provider=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(BUTTON_CANCEL)

    await OrderEditingChatsOrProviders.waiting_for_chat_id.set()
    await message.answer('Пропишите id чатов через запятую',
                         reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to '
                 f'{OrderEditingChatsOrProviders.waiting_for_chat_id}')


async def writing_provider(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get('chosen_situation') == ADD_PROVIDER:
        cur.execute(f"INSERT INTO providers(provider_desc) "
                    f"VALUES ('{message.text}')")
        connect.commit()
        await message.answer(f'Добавлен провайдер: {message.text}',
                             reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        return
    cur.execute(f"DELETE FROM providers "
                f"WHERE provider_desc = '{message.text}'")
    connect.commit()
    await message.answer(f'Провайдер удалён: {message.text}',
                         reply_markup=types.ReplyKeyboardRemove())
    await state.finish()
    return


async def writing_chat_id(message: types.Message, state: FSMContext):
    chat_id_parsed = message.text.split(',')
    user_data = await state.get_data('chosen_provider')
    chosen_provider = user_data.get('chosen_provider')
    cur.execute(f"SELECT id "
                f"FROM providers "
                f"WHERE provider_desc = '{chosen_provider}'")
    provider_parsed = cur.fetchone()[0]
    if user_data.get('chosen_situation') == ADD_CHAT:
        for i in chat_id_parsed:
            if int(i) and int(i) < 0:
                cur.execute(f"INSERT INTO chats(chat_id, provider_id) "
                            f"VALUES({i}, {provider_parsed})")
            else:
                chat_id_parsed.remove(i)
                await message.answer(f'{i} - некорректный id группы')
        connect.commit()
        await message.answer(f'Добавлены чаты: {chat_id_parsed}',
                             reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        return
    for i in chat_id_parsed:
        if int(i) and int(i) < 0:
            cur.execute(f"DELETE FROM chats "
                        f"WHERE chat_id = '{i}'")
        else:
            chat_id_parsed.remove(i)
            await message.answer(f'{i} - некорректный id группы')
    connect.commit()
    await message.answer(f'Удалены чаты: {chat_id_parsed}',
                         reply_markup=types.ReplyKeyboardRemove())
    await state.finish()
    return


def setup(dp: Dispatcher):
    """
    Регистрация хандлеров в диспетчере
    """
    dp.register_message_handler(start_editing_chats_or_providers,
                                commands='edit',
                                state=None)
    dp.register_message_handler(choice_of_situation,
                                state=OrderEditingChatsOrProviders.waiting_for_situation)
    dp.register_message_handler(choice_of_provider,
                                state=OrderEditingChatsOrProviders.waiting_for_provider)
    dp.register_message_handler(writing_chat_id,
                                state=OrderEditingChatsOrProviders.waiting_for_chat_id)
    dp.register_message_handler(writing_provider,
                                state=OrderEditingChatsOrProviders.waiting_for_write_provider)
