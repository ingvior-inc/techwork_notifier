import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.const import (HAPPENED_FAILUTE_RESOLVE,
                       HAPPENED_TECHNICAL_WORK_RESOLVE, PROVIDER,
                       DATE_AND_TIME, BUTTON_NOW, BUTTON_CANCEL,
                       USE_KEYBOARD_PLEASE)
from app.functions import white_list, notification_sender, get_current_time
from app.settings import situations, providers
from app.states import OrderBuildingNotif


async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Позволяет завершить работу на любом этапе цикла до рассылки
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'cancelling state {current_state}')

    await state.finish()

    await message.reply('Операция отменена. \n'
                        'Пропишите /start, чтобы начать заново',
                        reply_markup=types.ReplyKeyboardRemove())


@white_list
async def start_building_notif(message: types.Message):
    """
    Первый этап сборки сообщения для рассылки. Выбор ситуации: сбой или работы
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in situations:
        keyboard.add(i)
    keyboard.add(BUTTON_CANCEL)

    await OrderBuildingNotif.waiting_for_situation.set()
    await message.answer('О чём хотим сообщить?', reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to {OrderBuildingNotif.waiting_for_situation}')


async def choice_of_situation(message: types.Message, state: FSMContext):
    """
    Второй этап:
    1. Проверка выбранной ситуации на корректность и сохранение
    2. Выбор провайдера
    """
    if message.text not in situations:
        await message.answer(USE_KEYBOARD_PLEASE)
        return

    await state.update_data(chosen_situation=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in providers:
        keyboard.add(i)
    keyboard.add(BUTTON_CANCEL)

    await OrderBuildingNotif.next()
    await message.answer('У кого?', reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to {OrderBuildingNotif.waiting_for_provider}')


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
        await message.answer(USE_KEYBOARD_PLEASE)
        return

    await state.update_data(chosen_provider=message.text)

    ##########################################################################
    # Проверка на ситуацию: если сбой или работы завершены, то разослать текст
    # и закончить state-машину
    user_data = await state.get_data()

    if (user_data.get('chosen_situation')
            in (HAPPENED_FAILUTE_RESOLVE, HAPPENED_TECHNICAL_WORK_RESOLVE)):

        time_now = await get_current_time()
        situation_text_split = user_data.get('chosen_situation').split(' ')
        final_text = (f"<em>{situation_text_split[0]}</em> "
                      f"у {user_data.get('chosen_provider')} "
                      f"{situation_text_split[1]} на момент "
                      f"{time_now}")

        await notification_sender(message, state, user_data, final_text)
        return
    ##########################################################################

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(BUTTON_NOW)
    keyboard.add(BUTTON_CANCEL)

    await OrderBuildingNotif.next()
    await message.answer('Когда?', reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to {OrderBuildingNotif.waiting_for_date_and_time}')


async def writing_date_and_time(message: types.Message, state: FSMContext):
    """
    Четвёртый этап:
    1. Сохранение прописанных даты и времени
    2. Запрос описания: пишется вручную
    """
    if message.text == BUTTON_NOW:
        time_now = await get_current_time()
        await state.update_data(written_date_and_time=(f'{BUTTON_NOW} '
                                                       f'({time_now})'))
    else:
        await state.update_data(written_date_and_time=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(BUTTON_CANCEL)

    await OrderBuildingNotif.next()
    await message.answer('Опишите ситуацию', reply_markup=keyboard)

    logging.info(f'{message.chat.username}({message.chat.id}) '
                 f'switched to {OrderBuildingNotif.waiting_for_description}')


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

    final_text = (f"<em>{user_data.get('chosen_situation')}</em> \n\n"
                  f"{PROVIDER}{user_data.get('chosen_provider')} \n"
                  f"{DATE_AND_TIME}"
                  f"{user_data.get('written_date_and_time')} \n\n"
                  f"{user_data.get('written_description')}")

    await notification_sender(message, state, user_data, final_text)
    return


def setup(dp: Dispatcher):
    """
    Регистрация хандлеров в диспетчере
    """
    dp.register_message_handler(cancel_handler, commands='cancel', state='*')
    dp.register_message_handler(cancel_handler,
                                Text(equals=BUTTON_CANCEL, ignore_case=True),
                                state='*')
    dp.register_message_handler(start_building_notif,
                                commands=('start', 'help'), state=None)
    dp.register_message_handler(choice_of_situation,
                                state=OrderBuildingNotif.waiting_for_situation)
    dp.register_message_handler(choice_of_provider,
                                state=OrderBuildingNotif.waiting_for_provider)
    dp.register_message_handler(writing_date_and_time,
                                state=OrderBuildingNotif.waiting_for_date_and_time)
    dp.register_message_handler(writing_description,
                                state=OrderBuildingNotif.waiting_for_description)
