from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

import database as db
from config import DEFAULT_CHANNELS
from keyboards import channels_menu_kb, cancel_kb

router = Router()


class ChannelStates(StatesGroup):
    waiting_for_channel = State()


def channels_text(channels: list[str]) -> str:
    if not channels:
        return (
            "📢 <b>Каналы для поиска</b>\n\n"
            "У вас нет добавленных каналов.\n"
            "Добавьте Telegram-каналы с вакансиями."
        )
    ch_list = "\n".join(f"  • @{ch}" for ch in channels)
    return (
        f"📢 <b>Каналы для поиска</b> ({len(channels)} шт.)\n\n"
        f"{ch_list}\n\n"
        "Нажмите на канал, чтобы удалить его."
    )


@router.message(Command("channels"))
@router.message(F.text == "📢 Мои каналы")
async def show_channels(message: Message):
    channels = db.get_channels(message.from_user.id)
    await message.answer(
        channels_text(channels),
        reply_markup=channels_menu_kb(channels),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "add_channel")
async def ask_channel(callback: CallbackQuery, state: FSMContext):
    default_list = "\n".join(f"  • <code>{ch}</code>" for ch in DEFAULT_CHANNELS[:5])
    await callback.message.edit_text(
        "✏️ Введите username канала или группы <b>без символа @</b>.\n\n"
        f"<b>Примеры каналов с вакансиями:</b>\n{default_list}\n\n"
        "⚠️ Бот должен быть участником приватных каналов или канал должен быть публичным.",
        reply_markup=cancel_kb(),
        parse_mode="HTML",
    )
    await state.set_state(ChannelStates.waiting_for_channel)
    await callback.answer()


@router.message(ChannelStates.waiting_for_channel)
async def save_channel(message: Message, state: FSMContext):
    channel = message.text.strip().lstrip("@")

    if not channel.replace("_", "").isalnum():
        await message.answer(
            "⚠️ Некорректный username. Используйте только буквы, цифры и подчёркивание."
        )
        return

    added = db.add_channel(message.from_user.id, channel)
    await state.clear()

    channels = db.get_channels(message.from_user.id)
    if added:
        text = f"✅ Канал <b>@{channel}</b> добавлен!\n\n" + channels_text(channels)
    else:
        text = f"⚠️ Канал <b>@{channel}</b> уже есть в списке.\n\n" + channels_text(channels)

    await message.answer(text, reply_markup=channels_menu_kb(channels), parse_mode="HTML")


@router.callback_query(F.data.startswith("del_ch:"))
async def delete_channel(callback: CallbackQuery):
    channel = callback.data.split(":", 1)[1]
    db.remove_channel(callback.from_user.id, channel)
    channels = db.get_channels(callback.from_user.id)
    await callback.message.edit_text(
        f"🗑 Канал <b>@{channel}</b> удалён.\n\n" + channels_text(channels),
        reply_markup=channels_menu_kb(channels),
        parse_mode="HTML",
    )
    await callback.answer("Удалено")


@router.callback_query(F.data == "cancel")
async def cancel_channel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    channels = db.get_channels(callback.from_user.id)
    await callback.message.edit_text(
        channels_text(channels),
        reply_markup=channels_menu_kb(channels),
        parse_mode="HTML",
    )
    await callback.answer()
