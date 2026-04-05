from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

import database as db
from keyboards import keywords_menu_kb, cancel_kb, main_menu_kb

router = Router()


class KeywordStates(StatesGroup):
    waiting_for_keyword = State()


def keywords_text(keywords: list[str]) -> str:
    if not keywords:
        return (
            "🏷 <b>Ключевые слова</b>\n\n"
            "У вас пока нет ключевых слов.\n"
            "Добавьте слова для поиска вакансий."
        )
    kw_list = "\n".join(f"  • <code>{kw}</code>" for kw in keywords)
    return (
        f"🏷 <b>Ключевые слова</b> ({len(keywords)} шт.)\n\n"
        f"{kw_list}\n\n"
        "Нажмите на слово, чтобы удалить его."
    )


@router.message(Command("keywords"))
@router.message(F.text == "🏷 Мои ключевые слова")
async def show_keywords(message: Message):
    keywords = db.get_keywords(message.from_user.id)
    await message.answer(
        keywords_text(keywords),
        reply_markup=keywords_menu_kb(keywords),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "add_keyword")
async def ask_keyword(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "✏️ Введите ключевое слово или фразу для поиска вакансий.\n\n"
        "<i>Примеры: Python, удалённо, CAD инженер, SolidWorks</i>",
        reply_markup=cancel_kb(),
        parse_mode="HTML",
    )
    await state.set_state(KeywordStates.waiting_for_keyword)
    await callback.answer()


@router.message(KeywordStates.waiting_for_keyword)
async def save_keyword(message: Message, state: FSMContext):
    keyword = message.text.strip()
    if len(keyword) < 2:
        await message.answer("⚠️ Слишком короткое слово. Введите хотя бы 2 символа.")
        return
    if len(keyword) > 50:
        await message.answer("⚠️ Слишком длинное слово. Максимум 50 символов.")
        return

    added = db.add_keyword(message.from_user.id, keyword)
    await state.clear()

    keywords = db.get_keywords(message.from_user.id)
    if added:
        text = f"✅ Ключевое слово <b>{keyword}</b> добавлено!\n\n" + keywords_text(keywords)
    else:
        text = f"⚠️ Слово <b>{keyword}</b> уже есть в вашем списке.\n\n" + keywords_text(keywords)

    await message.answer(text, reply_markup=keywords_menu_kb(keywords), parse_mode="HTML")


@router.callback_query(F.data.startswith("del_kw:"))
async def delete_keyword(callback: CallbackQuery):
    keyword = callback.data.split(":", 1)[1]
    db.remove_keyword(callback.from_user.id, keyword)
    keywords = db.get_keywords(callback.from_user.id)
    await callback.message.edit_text(
        f"🗑 Слово <b>{keyword}</b> удалено.\n\n" + keywords_text(keywords),
        reply_markup=keywords_menu_kb(keywords),
        parse_mode="HTML",
    )
    await callback.answer("Удалено")


@router.callback_query(F.data == "clear_keywords")
async def clear_keywords(callback: CallbackQuery):
    db.clear_keywords(callback.from_user.id)
    await callback.message.edit_text(
        "🗑 Все ключевые слова удалены.\n\n" + keywords_text([]),
        reply_markup=keywords_menu_kb([]),
        parse_mode="HTML",
    )
    await callback.answer("Очищено")


@router.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    keywords = db.get_keywords(callback.from_user.id)
    await callback.message.edit_text(
        keywords_text(keywords),
        reply_markup=keywords_menu_kb(keywords),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()
