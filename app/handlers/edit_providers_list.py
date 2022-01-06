import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from app.const import Buttons, MessageParts
from app.general_functions import (white_list, get_providers_list,
                                   create_iter_keyboard)
from app.settings import cur, connect
from app.states import OrderEditingProviders as States

buttons = (Buttons.ADD_PROVIDER, Buttons.DELETE_PROVIDER)


@white_list
async def start_editing_providers(message: types.Message) -> None:
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
    user_data = await state.get_data()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(Buttons.CANCEL)

    if user_data.get('chosen_situation') == Buttons.DELETE_PROVIDER:
        keyboard = await create_iter_keyboard(await get_providers_list(
            with_default=False))

    await States.waiting_for_write_provider.set()
    await message.answer(MessageParts.WAITING_FOR_WRITING_PROVIDER,
                         reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to '
                 f'{States.waiting_for_write_provider=}')


async def writing_provider(message: types.Message, state: FSMContext) -> None:
    user_data = await state.get_data()

    if user_data.get('chosen_situation') == Buttons.DELETE_PROVIDER:
        if message.text not in await get_providers_list(with_default=False):
            await message.answer(MessageParts.USE_KEYBOARD_PLEASE)
            return
        cur.execute(f"DELETE FROM providers "
                    f"WHERE provider_desc = '{message.text}'")

    else:
        cur.execute(f"INSERT INTO providers(provider_desc) "
                    f"VALUES ('{message.text}') ON CONFLICT DO NOTHING ")

    connect.commit()

    await message.answer(f"{MessageParts.DONE}"
                         f" - {user_data.get('chosen_situation')}\n"
                         f" - {message.text}",
                         reply_markup=types.ReplyKeyboardRemove())

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'finished scenario "edit_providers_list"')

    await state.finish()


async def setup(dp: Dispatcher) -> None:
    """
    Registering handlers in Dispatcher.
    """
    dp.register_message_handler(start_editing_providers,
                                commands='edit_providers',
                                state=None)
    dp.register_message_handler(choice_of_situation,
                                state=States.waiting_for_situation)
    dp.register_message_handler(writing_provider,
                                state=States.waiting_for_write_provider)
