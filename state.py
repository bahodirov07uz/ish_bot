from aiogram.fsm.state import StatesGroup, State

class IshFSM(StatesGroup):
    ishchi = State()
    ish_nomi = State()
    soni = State()

from aiogram.fsm.state import State, StatesGroup

class RegisterState(StatesGroup):
    waiting_for_name = State()
    waiting_for_job = State()
    waiting_for_count = State()
