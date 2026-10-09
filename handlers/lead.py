import logging
from datetime import datetime, timedelta, timezone

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import load_config
from keyboards.services import services_keyboard
from states.lead import LeadForm
from storage import save_lead
from validators import (
    is_valid_email,
    is_valid_phone,
    is_valid_telegram_username,
)


logger = logging.getLogger(__name__)
router = Router(name=__name__)


# Настраиваем московское время и русские названия месяцев.
# Configure Moscow time and Russian month names.
MOSCOW_TZ = timezone(timedelta(hours=3), name="МСК")

RUSSIAN_MONTHS = (
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
)


# Форматируем дату в удобном для уведомления виде.
# Format the date for a readable notification.
def format_moscow_datetime(value: datetime) -> str:
    moscow_time = value.astimezone(MOSCOW_TZ)
    month = RUSSIAN_MONTHS[moscow_time.month - 1]

    return (
        f"{moscow_time:%H:%M}, "
        f"{moscow_time.day} {month} {moscow_time.year} года (МСК)"
    )


# Создаём кнопки подтверждения и отмены заявки.
# Create the lead confirmation and cancellation buttons.
def confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data="lead:confirm",
                ),
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data="lead:cancel",
                ),
            ]
        ]
    )


# Создаём кнопку перехода к профилю клиента.
# Create a button that opens the client's Telegram profile.
def telegram_profile_keyboard(
    user_id: int,
    username: str | None,
) -> InlineKeyboardMarkup:
    if username:
        profile_url = f"https://t.me/{username}"
    else:
        profile_url = f"tg://user?id={user_id}"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть профиль в Telegram",
                    url=profile_url,
                )
            ]
        ]
    )


@router.message(CommandStart())
async def start_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()

    # Загружаем и проверяем конфигурацию.
    # Load and validate the configuration.
    try:
        config = load_config()
    except (OSError, ValueError, RuntimeError):
        logger.exception("Не удалось загрузить конфигурацию бота.")
        await message.answer(
            "Не удалось загрузить настройки бота. Попробуйте позже."
        )
        return

    await state.set_state(LeadForm.service)

    await message.answer(
        config["welcome_message"],
        reply_markup=services_keyboard(config["services"]),
    )


@router.message(Command("cancel"))
async def cancel_handler(
    message: Message,
    state: FSMContext,
) -> None:
    current_state = await state.get_state()

    if current_state is None:
        await message.answer("Сейчас нет активной заявки.")
        return

    await state.clear()
    await message.answer("Заполнение заявки отменено.")


@router.callback_query(
    LeadForm.service,
    F.data.startswith("service:"),
)
async def service_handler(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    service = (callback.data or "").removeprefix("service:")

    # Проверяем выбранную услугу по конфигурации.
    # Validate the selected service against the configuration.
    try:
        config = load_config()
    except (OSError, ValueError, RuntimeError):
        logger.exception("Не удалось загрузить конфигурацию.")
        await callback.answer(
            "Не удалось загрузить настройки бота.",
            show_alert=True,
        )
        return

    if service not in config["services"]:
        await callback.answer(
            "Эта услуга больше недоступна.",
            show_alert=True,
        )
        return

    await callback.answer()
    await state.update_data(service=service)
    await state.set_state(LeadForm.name)

    if isinstance(callback.message, Message):
        await callback.message.answer("Введите ваше имя:")


@router.message(LeadForm.service)
async def service_fallback(message: Message) -> None:
    await message.answer(
        "Пожалуйста, выберите услугу кнопкой выше."
    )


@router.message(LeadForm.name, F.text)
async def name_handler(
    message: Message,
    state: FSMContext,
) -> None:
    name = (message.text or "").strip()

    # Проверяем только длину имени и наличие хотя бы одной буквы.
    # Validate only the name length and require at least one letter.
    if (
        len(name) < 2
        or len(name) > 100
        or not any(char.isalpha() for char in name)
    ):
        await message.answer(
            "Введите имя длиной от 2 до 100 символов, "
            "содержащее хотя бы одну букву."
        )
        return

    await state.update_data(name=name)
    await state.set_state(LeadForm.contact)

    await message.answer(
        "Введите контакт: телефон, @username или email.\n"
        "Можно указать свой Telegram ID."
    )


@router.message(LeadForm.name)
async def name_fallback(message: Message) -> None:
    await message.answer(
        "Пожалуйста, отправьте имя обычным текстовым сообщением."
    )


@router.message(LeadForm.contact, F.text)
async def contact_handler(
    message: Message,
    state: FSMContext,
) -> None:
    contact = (message.text or "").strip()
    user = message.from_user

    # Разрешаем указать собственный Telegram ID.
    # Allow the user to provide their own Telegram ID.
    is_telegram_id = (
        user is not None
        and contact == str(user.id)
    )

    # Проверяем остальные варианты контактных данных.
    # Validate the other contact information formats.
    is_valid_contact = (
        is_valid_phone(contact)
        or is_valid_telegram_username(contact)
        or is_valid_email(contact)
    )

    if not is_telegram_id and not is_valid_contact:
        await message.answer(
            "Не удалось распознать контакт.\n"
            "Отправьте корректный телефон, @username или email. "
            "Также можно указать свой Telegram ID."
        )
        return

    await state.update_data(contact=contact)
    await state.set_state(LeadForm.confirmation)

    data = await state.get_data()

    # Показываем заявку перед подтверждением.
    # Display the lead before asking for confirmation.
    await message.answer(
        "Проверьте данные заявки:\n\n"
        f"Услуга: {data['service']}\n"
        f"Имя: {data['name']}\n"
        f"Контакт: {data['contact']}\n\n"
        "Подтвердить отправку заявки?",
        reply_markup=confirmation_keyboard(),
    )


@router.message(LeadForm.contact)
async def contact_fallback(message: Message) -> None:
    await message.answer(
        "Пожалуйста, отправьте контакт текстом: "
        "телефон, @username или email."
    )


@router.callback_query(
    LeadForm.confirmation,
    F.data == "lead:confirm",
)
async def confirmation_handler(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    data = await state.get_data()

    # Проверяем наличие всех обязательных данных.
    # Validate that all required lead fields are present.
    required_fields = ("service", "name", "contact")

    if any(
        not isinstance(data.get(field), str) or not data[field].strip()
        for field in required_fields
    ):
        await state.clear()
        await callback.answer(
            "Данные заявки потеряны. Начните заполнение заново.",
            show_alert=True,
        )
        return

    user = callback.from_user
    username = user.username
    username_label = f"@{username}" if username else None
    contact = data["contact"].strip()
    user_id = user.id

    # Определяем, совпадает ли указанный контакт с Telegram-профилем.
    # Determine whether the submitted contact matches the Telegram profile.
    contact_is_user_id = contact == str(user_id)

    contact_is_username = (
        username is not None
        and contact.removeprefix("@").casefold() == username.casefold()
    )

    # Исключаем повторение одинаковых контактных данных в уведомлении.
    # Avoid duplicating identical contact information in the notification.
    if contact_is_user_id or contact_is_username:
        if username_label:
            contact_lines = [
                f"Telegram: {username_label} (ID: {user_id})"
            ]
        else:
            contact_lines = [f"Telegram ID: {user_id}"]
    else:
        contact_lines = [f"Контакт для связи: {contact}"]

        if username_label:
            contact_lines.append(
                f"Telegram: {username_label} (ID: {user_id})"
            )
        else:
            contact_lines.append(f"Telegram ID: {user_id}")

    # Сохраняем время создания заявки в UTC для файла.
    # Store the lead creation time in UTC for the data file.
    created_at = datetime.now(timezone.utc)

    lead = {
        "service": data["service"],
        "name": data["name"],
        "contact": contact,
        "user_id": user_id,
        "telegram_username": username,
        "created_at": created_at.isoformat(timespec="seconds"),
    }

    # Сохраняем заявку до отправки уведомления администратору.
    # Save the lead before notifying the administrator.
    try:
        config = load_config()
        save_lead(lead)
    except (OSError, ValueError, RuntimeError, TypeError):
        logger.exception(
            "Не удалось сохранить заявку пользователя %s.",
            user_id,
        )
        await callback.answer(
            "Не удалось сохранить заявку. Попробуйте ещё раз.",
            show_alert=True,
        )
        return

    await state.clear()
    await callback.answer("Заявка сохранена.")

    # Формируем уведомление с московским временем.
    # Build the notification using Moscow time.
    moscow_datetime = format_moscow_datetime(created_at)

    admin_text = "\n".join(
        [
            "Новая заявка",
            "",
            f"Услуга: {lead['service']}",
            f"Имя: {lead['name']}",
            *contact_lines,
            f"Дата: {moscow_datetime}",
        ]
    )

    # Отправляем уведомление администратору вместе со ссылкой на профиль.
    # Send the notification with a link to the client's profile.
    try:
        await callback.bot.send_message(
            chat_id=config["admin_id"],
            text=admin_text,
            reply_markup=telegram_profile_keyboard(
                user_id=user_id,
                username=username,
            ),
        )
        admin_notified = True
    except Exception:
        admin_notified = False
        logger.exception(
            "Не удалось отправить заявку администратору %s.",
            config["admin_id"],
        )

    # Сообщаем пользователю результат и убираем кнопки подтверждения.
    # Notify the user and remove the confirmation buttons.
    if isinstance(callback.message, Message):
        if admin_notified:
            result_text = (
                "Спасибо! Заявка сохранена и отправлена администратору."
            )
        else:
            result_text = (
                "Заявка сохранена, но уведомление администратору "
                "не отправлено. Ошибка записана в журнал."
            )

        try:
            await callback.message.edit_text(
                result_text,
                reply_markup=None,
            )
        except Exception:
            logger.exception(
                "Не удалось обновить сообщение после подтверждения."
            )


@router.callback_query(
    LeadForm.confirmation,
    F.data == "lead:cancel",
)
async def confirmation_cancel_handler(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    # Отменяем заявку без записи в файл.
    # Cancel the lead without saving it to the file.
    await state.clear()
    await callback.answer("Заявка отменена.")

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            "Заполнение заявки отменено.",
            reply_markup=None,
        )