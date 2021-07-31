import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.settings import bot, CHAT_ID
from app.states import OrderBuildingNotif
from app.white_list import white_list
from app.message_parts import (PROVIDER_SELF, PROVIDER_TKB,
                               PROVIDER_FORTA_TECH, PROVIDER_BRS, PROVIDER,
                               DATE_AND_TIME, DESCRIPTION, situations,
                               providers)


dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Операция отменена',
                        reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['start', 'help'], state=None)
@white_list
async def start_building_notif(message: types.Message):

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in situations:
        keyboard.add(i)
    keyboard.add('Отмена')

    await message.answer('О чём хотим сообщить?', reply_markup=keyboard)
    await OrderBuildingNotif.waiting_for_situation.set()


@dp.message_handler(state=OrderBuildingNotif.waiting_for_situation)
async def choice_of_situation(message: types.Message, state: FSMContext):
    if message.text not in situations:
        await message.answer('Выберите ситуацию с помощью клавиатуры')
        return

    await state.update_data(chosen_situation=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in providers:
        keyboard.add(i)
    keyboard.add('Отмена')

    await OrderBuildingNotif.next()
    await message.answer('У кого намечается?', reply_markup=keyboard)


@dp.message_handler(state=OrderBuildingNotif.waiting_for_provider)
async def choice_of_provider(message: types.Message, state: FSMContext):
    if message.text not in providers:
        await message.answer('Некорректный провайдер')
        return

    await state.update_data(chosen_provider=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Сейчас')
    keyboard.add('Отмена')

    await OrderBuildingNotif.next()
    await message.answer('Когда?', reply_markup=keyboard)


@dp.message_handler(state=OrderBuildingNotif.waiting_for_date_and_time)
async def writing_date_and_time(message: types.Message, state: FSMContext):

    await state.update_data(written_date_and_time=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Отмена')

    await OrderBuildingNotif.next()
    await message.answer('Опишите ситуацию', reply_markup=keyboard)


@dp.message_handler(state=OrderBuildingNotif.waiting_for_custom_text)
async def writing_about(message: types.Message, state: FSMContext):

    await state.update_data(custom_text=message.text)

    user_data = await state.get_data()

    final_text = (f"<b>{user_data.get('chosen_situation')}</b> \n\n"
                  f"<b>{PROVIDER}</b>{user_data.get('chosen_provider')} \n"
                  f"<b>{DATE_AND_TIME}</b>{user_data.get('written_date_and_time')} \n"
                  f"<b>{DESCRIPTION}</b>{user_data.get('custom_text')}")

    if user_data.get('chosen_provider') == PROVIDER_SELF:
        for i in CHAT_ID[PROVIDER_SELF]:
            await message.bot.send_message(chat_id=i, text=final_text)

    elif user_data.get('chosen_provider') == PROVIDER_TKB:
        for i in CHAT_ID[PROVIDER_TKB]:
            await message.bot.send_message(chat_id=i, text=final_text)

    elif user_data.get('chosen_provider') == PROVIDER_FORTA_TECH:
        for i in CHAT_ID[PROVIDER_FORTA_TECH]:
            await message.bot.send_message(chat_id=i, text=final_text)

    elif user_data.get('chosen_provider') == PROVIDER_BRS:
        for i in CHAT_ID[PROVIDER_BRS]:
            await message.bot.send_message(chat_id=i, text=final_text)

    await message.answer('Разослали', reply_markup=types.ReplyKeyboardRemove())

    await state.finish()
