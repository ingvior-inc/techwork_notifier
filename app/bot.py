import logging

from aiogram import Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import ChatNotFound, ChatIdIsEmpty

from app.settings import bot, chat_id
from app.states import OrderBuildingNotif
from app.text_parts import (HAPPENED_FAILUTE_RESOLVE,
                            HAPPENED_TECHNICAL_WORK_RESOLVE, PROVIDER,
                            DATE_AND_TIME, situations, providers)
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

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'cancelling state {current_state}')
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

    logging.info(f'{message.chat.username}({message.chat.id}) '
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
    await message.answer('У кого?', reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to {OrderBuildingNotif.waiting_for_provider}')


@dp.message_handler(state=OrderBuildingNotif.waiting_for_provider)
async def choice_of_provider(message: types.Message, state: FSMContext):
    """
    Третий этап:
    1. Проверка выбранного провайдера на корректность и сохранение
    2. Проверка выбранной ситуации: если это конец работ или сбоя, то
    отправляется соответствующая рассылка по выбранному провайдеру,
    цикл завершается досрочно.
    3. Запрос даты и времени: поставить Сейчас по кнопке или написать вручную
    """
    if message.text not in providers:
        await message.answer('Некорректный провайдер. \n'
                             'Выберите с помощью клавиатуры')
        return

    await state.update_data(chosen_provider=message.text)

    # Проверка на ситуацию: если сбой или работы завершены, то разослать текст
    # и закончить state-машину
    user_data = await state.get_data()

    if (user_data.get('chosen_situation')
            in (HAPPENED_FAILUTE_RESOLVE, HAPPENED_TECHNICAL_WORK_RESOLVE)):

        final_text = (f"{user_data.get('chosen_situation')}\n\n"
                      f"{PROVIDER}{user_data.get('chosen_provider')}")

        chats_recipients = []

        for i in chat_id[user_data.get('chosen_provider')]:
            try:
                sended = await message.bot.send_message(chat_id=i,
                                                        text=final_text)
                chats_recipients.append(sended.chat.title)
                logging.info(f'Message has been sent to "{sended.chat.title}"'
                             f'({sended.chat.id})')
            except (ChatNotFound, ChatIdIsEmpty):
                await message.answer(f'Группа с id {i} не найдена')
                logging.error(f'ID {i} - group not found exception')

        await message.answer(f'Текст отправлен в чаты: \n\n'
                             f'{chats_recipients} \n\n'
                             f'Содержание:\n\n{final_text}',
                             reply_markup=types.ReplyKeyboardRemove())

        logging.info(f'{message.chat.username}({message.chat.id}) '
                     f'completed the last stage')

        await state.finish()
        return
    #

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Сейчас')
    keyboard.add('Отмена')

    await OrderBuildingNotif.next()
    await message.answer('Когда?', reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
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

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to {OrderBuildingNotif.waiting_for_description}')


@dp.message_handler(state=OrderBuildingNotif.waiting_for_description)
async def writing_description(message: types.Message, state: FSMContext):
    """
    Пятый этап:
    1. Сохранение описания
    2. Сборка текста на основе выбранных ранее параметров
    3. Рассылка сообщений по чатам в зависимости от выбранного  провайдера
    4. Завершение работы
    """
    await state.update_data(written_description=message.text)

    user_data = await state.get_data()

    final_text = (f"{user_data.get('chosen_situation')} \n\n"
                  f"{PROVIDER}{user_data.get('chosen_provider')} \n"
                  f"{DATE_AND_TIME}"
                  f"{user_data.get('written_date_and_time')} \n\n"
                  f"{user_data.get('written_description')}")

    chats_recipients = []

    for i in chat_id[user_data.get('chosen_provider')]:
        try:
            sended = await message.bot.send_message(chat_id=i, text=final_text)
            chats_recipients.append(sended.chat.title)
            logging.info(f'Message has been sent to "{sended.chat.title}"'
                         f'({sended.chat.id})')
        except (ChatNotFound, ChatIdIsEmpty):
            await message.answer(f'Группа с id {i} не найдена')
            logging.error(f'ID {i} - group not found exception')

    await message.answer(f'Текст отправлен в чаты: \n\n'
                         f'{chats_recipients} \n\n'
                         f'Содержание:\n\n{final_text}',
                         reply_markup=types.ReplyKeyboardRemove())

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'completed the last stage')

    await state.finish()
