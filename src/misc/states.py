"""
=====
States
=====

Defines states fro this bot
"""
from aiogram.fsm.state import State, StatesGroup

class States(StatesGroup):
    mainState = State()
    inputState = State()
    confirmationState = State()