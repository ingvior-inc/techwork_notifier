import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from app.const import Buttons, MessageParts
from app.general_functions import (white_list, get_admins_list,
                                   create_iter_keyboard)
from app.settings import cur, connect
from app.states import OrderEditingWhiteList as States

buttons = [Buttons.ADD_ADMIN, Buttons.DELETE_ADMIN]


@white_list
async def check_admin_list(message: types.Message):
    admin_list = await get_admins_list()
    await message.answer(f'Список админов:\n\n'
                         f'{admin_list}')


@white_list
async def start_editing_white_list(message: types.Message):
    keyboard = await create_iter_keyboard(buttons)

    await States.waiting_for_situation.set()
    await message.answer('Что хотим сделать?', reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to '
                 f'{States.waiting_for_situation=}')


async def choice_of_situation(message: types.Message, state: FSMContext):
    if message.text not in buttons:
        await message.answer(MessageParts.USE_KEYBOARD_PLEASE)
        return

    await state.update_data(chosen_situation=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(Buttons.CANCEL)

    await States.next()
    await message.answer('Укажите id админа',
                         reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to '
                 f'{States.waiting_for_chat_id=}')


async def writing_chat_id(message: types.Message, state: FSMContext):
    user_data = await state.get_data('chosen_situation')
    if user_data.get('chosen_situation') == Buttons.ADD_ADMIN:
        cur.execute(f'INSERT INTO white_list(chat_id) '
                    f'VALUES ({int(message.text)}) ON CONFLICT DO NOTHING ')

    else:
        cur.execute(f'DELETE FROM white_list '
                    f'WHERE chat_id = {int(message.text)}')

    connect.commit()

    await message.answer(f"{MessageParts.DONE}"
                         f" - {user_data.get('chosen_situation')}\n"
                         f" - {message.text}",
                         reply_markup=types.ReplyKeyboardRemove())

    await state.finish()


async def setup(dp: Dispatcher):
    """
    Registering handlers in Dispatcher.
    """
    dp.register_message_handler(start_editing_white_list,
                                commands='whoisyourdaddy',
                                state=None)
    dp.register_message_handler(choice_of_situation,
                                state=States.waiting_for_situation)
    dp.register_message_handler(writing_chat_id,
                                state=States.waiting_for_chat_id)
    dp.register_message_handler(check_admin_list,
                                commands='iseedeadpeoples',
                                state=None)
