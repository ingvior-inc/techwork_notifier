import logging

accepted_user_id = (512309881, )


def white_list(func):
    # Ботом могут пользоваться только одобренные партией пользователи
    async def wrapper(message):
        if message.chat.id in accepted_user_id:
            logging.info(f'{message.chat.username}({message.chat.id}) - accepted')
            return await func(message)
        # Вызовы к боту из групп игнорировать
        elif message.chat.id < 0:
            logging.info(f'{message.chat.title}({message.chat.id}): - is group, ignored')
            return None
        else:
            logging.info(f'{message.chat.username}({message.chat.id}) - denied')
            await message.answer('Доступ запрещён')
    return wrapper
