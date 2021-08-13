import logging
import datetime

from aiogram import types
from aiogram.utils.exceptions import ChatNotFound, ChatIdIsEmpty

from app.settings import accepted_user_id, chat_id


def white_list(func):
    """
    Ботом могут пользоваться только одобренные партией пользователи.
    Декоратор таковых проверяет.
    """
    async def wrapper(message):
        if str(message.chat.id) in accepted_user_id:
            logging.warning(f'{message.chat.username}({message.chat.id})'
                            f' - accepted')
            return await func(message)
        # Вызовы к боту из групп игнорировать
        elif message.chat.id < 0:
            logging.warning(f'{message.chat.title}({message.chat.id}):'
                            f' - is group, ignored')
            return None
        else:
            logging.warning(f'{message.chat.username}({message.chat.id})'
                            f' - denied')
            await message.answer('Доступ запрещён')
    return wrapper


async def notification_sender(message, state, user_data, final_text):
    """
    Рассылка сообщений по чатам, в зависимости от выбранного провайдера.
    """
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


async def get_current_time():
    delta = datetime.timedelta(hours=3, minutes=0)
    now_utc_3 = datetime.datetime.now(datetime.timezone.utc) + delta
    return now_utc_3.strftime('%d.%m.%Y, %H:%M')
