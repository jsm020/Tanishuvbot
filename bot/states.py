from aiogram.fsm.state import StatesGroup, State

class RegisterStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_location = State()
