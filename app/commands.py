from aiogram import Dispatcher
from aiogram.types import BotCommand

commands = {
    'start': 'Инициация бота',
    'edit': 'Редактирование списка чатов/провайдеров',
    'check_list': 'Текущий список чатов/провайдеров',
    'cancel': 'Отмена текущей операции'
}


async def set_commands(dp: Dispatcher):
    await dp.bot.set_my_commands(
        [BotCommand(command, description)
         for command, description in commands.items()]
    )
