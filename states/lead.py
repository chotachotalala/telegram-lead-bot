from aiogram.fsm.state import State, StatesGroup


class LeadForm(StatesGroup):
    """Этапы заполнения заявки."""

    service = State()
    name = State()
    contact = State()