import logging

from app.settings import accepted_user_ids


def white_list(func):
    """
    Ботом могут пользоваться только одобренные партией пользователи.
    Декоратор таковых проверяет.
    """
    async def wrapper(message):
        if message.chat.id in accepted_user_ids:
            logging.info(f'{message.chat.username}({message.chat.id})'
                         f' - accepted')
            return await func(message)
        # Вызовы к боту из групп игнорировать
        elif message.chat.id < 0:
            logging.info(f'{message.chat.title}({message.chat.id}):'
                         f' - is group, ignored')
            return None
        else:
            logging.info(f'{message.chat.username}({message.chat.id})'
                         f' - denied')
            await message.answer('Доступ запрещён')
    return wrapper
