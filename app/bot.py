import logging

from aiogram import Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.text_parts import (PROVIDER, DATE_AND_TIME, DESCRIPTION,
                            situations, providers)
from app.settings import bot, chat_ids
from app.states import OrderBuildingNotif
from app.white_list import white_list

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
    await message.reply('Операция отменена. \n'
                        'Пропишите /start, чтобы начать заново',
                        reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['start', 'help'], state=None)
@white_list
async def start_building_notif(message: types.Message):
    """
    Первый этап сборки сообщения для рассылки. Выбор ситуации: сбой или работы
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in situations:
        keyboard.add(i)
    keyboard.add('Отмена')

    await OrderBuildingNotif.waiting_for_situation.set()
    await message.answer('О чём хотим сообщить?', reply_markup=keyboard)

    logging.info(f'{message.chat.username} '
                 f'switched to {OrderBuildingNotif.waiting_for_situation}')


@dp.message_handler(state=OrderBuildingNotif.waiting_for_situation)
async def choice_of_situation(message: types.Message, state: FSMContext):
    """
    Второй этап:
    1. Проверка выбранной ситуации на корректность и сохранение
    2. Выбор провайдера
    """
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

    logging.info(f'{message.chat.username} '
                 f'switched to {OrderBuildingNotif.waiting_for_provider}')


@dp.message_handler(state=OrderBuildingNotif.waiting_for_provider)
async def choice_of_provider(message: types.Message, state: FSMContext):
    """
    Третий этап:
    1. Проверка выбранного провайдера на корректность и сохранение
    2. Запрос даты и времени: поставить Сейчас по кнопке или написать вручную
    """
    if message.text not in providers:
        await message.answer('Некорректный провайдер')
        return

    await state.update_data(chosen_provider=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Сейчас')
    keyboard.add('Отмена')

    await OrderBuildingNotif.next()
    await message.answer('Когда?', reply_markup=keyboard)

    logging.info(f'{message.chat.username} '
                 f'switched to {OrderBuildingNotif.waiting_for_date_and_time}')


@dp.message_handler(state=OrderBuildingNotif.waiting_for_date_and_time)
async def writing_date_and_time(message: types.Message, state: FSMContext):
    """
    Четвёртый этап:
    1. Сохранение прописанных даты и времени
    2. Запрос описания: пишется вручную
    """
    await state.update_data(written_date_and_time=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Отмена')

    await OrderBuildingNotif.next()
    await message.answer('Опишите ситуацию', reply_markup=keyboard)

    logging.info(f'{message.chat.username} '
                 f'switched to {OrderBuildingNotif.waiting_for_custom_text}')


@dp.message_handler(state=OrderBuildingNotif.waiting_for_custom_text)
async def writing_about(message: types.Message, state: FSMContext):
    """
    Пятый этап:
    1. Сохранение описания
    2. Сборка текста на основе сохранённых ранее параметров
    3. Рассылка сообщений по чатам в зависимости от выбранного  провайдера
    4. Завершение работы State-машины
    """
    await state.update_data(custom_text=message.text)

    user_data = await state.get_data()

    final_text = (f"<b>{user_data.get('chosen_situation')}</b> \n\n"
                  f"<b>{PROVIDER}</b>{user_data.get('chosen_provider')} \n"
                  f"<b>{DATE_AND_TIME}</b>"
                  f"{user_data.get('written_date_and_time')} \n"
                  f"<b>{DESCRIPTION}</b>{user_data.get('custom_text')}")

    chats_recipients = []

    for i in chat_ids[user_data.get('chosen_provider')]:
        sended = await message.bot.send_message(chat_id=i, text=final_text)
        chats_recipients.append(sended.chat.title)
        logging.info(f'Message has been sent to "{sended.chat.title}"'
                     f'({sended.chat.id})')

    await message.answer(f'Текст отправлен в чаты: \n\n'
                         f'{chats_recipients} \n\n'
                         f'Содержание:\n\n{final_text}',
                         reply_markup=types.ReplyKeyboardRemove())

    logging.info(f'{message.chat.username} '
                 f'completed the last stage')

    await state.finish()
