from aiogram.fsm.state import State, StatesGroup


class LeadForm(StatesGroup):
    service = State()
    name = State()
    contact = State()

    # Добавляем отдельный этап подтверждения заявки.
    # Add a separate lead confirmation state.
    confirmation = State()