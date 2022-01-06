from aiogram import Dispatcher
from aiogram.types import BotCommand

commands = {
    'start': 'Запустить рассылку',
    'end': 'Завершить инцидент',
    'del': 'Удалить сообщения по последней рассылке',
    'edit_recipients': 'Отредактировать список получателей',
    'edit_providers': 'Отредактировать список провайдеров',
    'check_recipients': 'Вывод списка получателей',
    'cancel': 'Отмена активной операции'
}


async def set_commands(dp: Dispatcher) -> None:
    """
    Adding commands and there description to Telegram UI.
    """
    await dp.bot.set_my_commands(
        [BotCommand(command, description)
         for command, description in commands.items()]
    )
