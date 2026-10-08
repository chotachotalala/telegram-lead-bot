from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import load_config
from keyboards.services import services_keyboard
from states.lead import LeadForm


router = Router(name=__name__)


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    """Начинает новую заявку."""

    # Если пользователь начал новую заявку,
    # удаляем данные и состояние предыдущей заявки.
    await state.clear()

    config = load_config()

    # После /start пользователь находится на этапе выбора услуги.
    await state.set_state(LeadForm.service)

    await message.answer(
        config["welcome_message"],
        reply_markup=services_keyboard(config["services"]),
    )


@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """Отменяет текущую заявку."""

    current_state = await state.get_state()

    if current_state is None:
        await message.answer("Сейчас нет активной заявки.")
        return

    await state.clear()

    await message.answer(
        "Заполнение заявки отменено."
    )


@router.callback_query(LeadForm.service, F.data.startswith("service:"))
async def service_handler(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Получает выбранную услугу и переходит к вводу имени."""

    callback_data = callback.data or ""

    # Из callback_data получаем текст выбранной услуги.
    service = callback_data.removeprefix("service:")

    config = load_config()

    # Проверяем, действительно ли такая услуга существует
    # в нашей конфигурации.
    if service not in config["services"]:
        await callback.answer(
            "Эта услуга больше недоступна.",
            show_alert=True,
        )
        return

    # Telegram показывает индикатор загрузки после нажатия
    # inline-кнопки. Этот вызов его убирает.
    await callback.answer()

    # Сохраняем выбранную услугу в данные FSM.
    await state.update_data(service=service)

    # Переходим к следующему этапу.
    await state.set_state(LeadForm.name)

    # В обычном личном чате callback.message существует.
    if callback.message:
        await callback.message.answer(
            "Введите ваше имя:"
        )


@router.message(LeadForm.service)
async def service_fallback(message: Message) -> None:
    """Обрабатывает текст вместо нажатия кнопки услуги."""

    await message.answer(
        "Пожалуйста, выберите услугу кнопкой выше."
    )


@router.message(LeadForm.name, F.text)
async def name_handler(
    message: Message,
    state: FSMContext,
) -> None:
    """Получает имя пользователя."""

    name = message.text.strip()

    # Примитивная учебная проверка имени:
    # минимум 2 символа, максимум 100 и хотя бы одна буква.
    if (
        len(name) < 2
        or len(name) > 100
        or not any(char.isalpha() for char in name)
    ):
        await message.answer(
            "Пожалуйста, введите настоящее имя текстом "
            "(минимум 2 символа)."
        )
        return

    # Сохраняем имя.
    await state.update_data(name=name)

    # Переходим к контакту.
    await state.set_state(LeadForm.contact)

    await message.answer(
        "Введите контакт: телефон, @username или email."
    )


@router.message(LeadForm.name)
async def name_fallback(message: Message) -> None:
    """Обрабатывает сообщения, которые не являются обычным текстом."""

    await message.answer(
        "Пожалуйста, отправьте имя обычным текстовым сообщением."
    )


@router.message(LeadForm.contact, F.text)
async def contact_handler(
    message: Message,
    state: FSMContext,
) -> None:
    """Получает контакт и завершает заполнение заявки."""

    contact = message.text.strip()

    # Проверяем несколько простых вариантов:
    # телефон, Telegram username или email.
    has_phone = sum(char.isdigit() for char in contact) >= 3
    has_username = contact.startswith("@") and len(contact) > 1
    has_email = "@" in contact and "." in contact

    if (
        len(contact) < 3
        or not (has_phone or has_username or has_email)
    ):
        await message.answer(
            "Не удалось распознать контакт.\n"
            "Отправьте телефон, @username или email."
        )
        return

    # Получаем текущие данные заявки и одновременно
    # добавляем в них контакт.
    data = await state.update_data(contact=contact)

    # Заявка закончена — состояние больше не нужно.
    await state.clear()

    await message.answer(
        "Спасибо! Заявка принята.\n\n"
        "Новая заявка:\n"
        f"Услуга: {data['service']}\n"
        f"Имя: {data['name']}\n"
        f"Контакт: {data['contact']}"
    )


@router.message(LeadForm.contact)
async def contact_fallback(message: Message) -> None:
    """Обрабатывает фото, голосовые и другие неожиданные сообщения."""

    await message.answer(
        "Пожалуйста, отправьте контакт текстом: "
        "телефон, @username или email."
    )