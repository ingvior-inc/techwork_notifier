from aiogram.dispatcher.filters.state import State, StatesGroup


class OrderBuildingNotif(StatesGroup):
    waiting_for_situation = State()
    waiting_for_provider = State()
    waiting_for_date_and_time = State()
    waiting_for_description = State()
