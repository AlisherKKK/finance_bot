from aiogram.fsm.state import State, StatesGroup


class TransactionStates(StatesGroup):
    """Состояния для добавления транзакций"""
    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_description = State()


class DebtStates(StatesGroup):
    """Состояния для добавления долгов"""
    waiting_for_person_name = State()
    waiting_for_amount = State()
    waiting_for_description = State()


class CategoryStates(StatesGroup):
    """Состояния для управления категориями"""
    waiting_for_new_category_name = State()
