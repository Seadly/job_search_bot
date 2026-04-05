from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🔍 Искать вакансии"),
        KeyboardButton(text="🏷 Мои ключевые слова"),
    )
    builder.row(
        KeyboardButton(text="📢 Мои каналы"),
        KeyboardButton(text="🔔 Уведомления"),
    )
    builder.row(KeyboardButton(text="ℹ️ Помощь"))
    return builder.as_markup(resize_keyboard=True)


def keywords_menu_kb(keywords: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for kw in keywords:
        builder.row(
            InlineKeyboardButton(text=f"❌ {kw}", callback_data=f"del_kw:{kw}")
        )
    builder.row(
        InlineKeyboardButton(text="➕ Добавить слово", callback_data="add_keyword"),
        InlineKeyboardButton(text="🗑 Очистить всё", callback_data="clear_keywords"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_main"))
    return builder.as_markup()


def channels_menu_kb(channels: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ch in channels:
        builder.row(
            InlineKeyboardButton(text=f"❌ @{ch}", callback_data=f"del_ch:{ch}")
        )
    builder.row(
        InlineKeyboardButton(text="➕ Добавить канал", callback_data="add_channel"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_main"))
    return builder.as_markup()


def alerts_kb(enabled: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if enabled:
        builder.row(InlineKeyboardButton(text="🔕 Выключить уведомления", callback_data="alerts_off"))
    else:
        builder.row(InlineKeyboardButton(text="🔔 Включить уведомления", callback_data="alerts_on"))
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_main"))
    return builder.as_markup()


def search_results_kb(has_more: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔍 Искать снова", callback_data="search_again"))
    builder.row(InlineKeyboardButton(text="⚙️ Настройки поиска", callback_data="back_main"))
    return builder.as_markup()


def cancel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    return builder.as_markup()
