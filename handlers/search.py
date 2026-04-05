import asyncio
import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

import database as db
from keyboards import search_results_kb
from telethon_searcher import search_vacancies

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("search"))
@router.message(F.text == "🔍 Искать вакансии")
async def cmd_search(message: Message, bot: Bot):
    user_id = message.from_user.id
    keywords = db.get_keywords(user_id)
    channels = db.get_channels(user_id)

    if not keywords:
        await message.answer(
            "⚠️ <b>Нет ключевых слов!</b>\n\n"
            "Добавьте слова через меню <i>🏷 Мои ключевые слова</i>.",
            parse_mode="HTML",
        )
        return

    if not channels:
        await message.answer(
            "⚠️ <b>Нет каналов для поиска!</b>\n\n"
            "Добавьте каналы через меню <i>📢 Мои каналы</i>.",
            parse_mode="HTML",
        )
        return

    kw_preview = ", ".join(f"<code>{kw}</code>" for kw in keywords[:5])
    if len(keywords) > 5:
        kw_preview += f" и ещё {len(keywords) - 5}…"

    status_msg = await message.answer(
        f"🔍 <b>Ищу вакансии…</b>\n\n"
        f"🏷 Слова: {kw_preview}\n"
        f"📢 Каналов: {len(channels)}\n\n"
        f"<i>Может занять несколько секунд…</i>",
        parse_mode="HTML",
    )

    try:
        vacancies, failed = await search_vacancies(
            channels=channels,
            keywords=keywords,
        )
    except RuntimeError as e:
        await status_msg.edit_text(
            f"❌ <b>Ошибка конфигурации:</b>\n<code>{e}</code>",
            parse_mode="HTML",
        )
        return
    except Exception as e:
        logger.error("Search error: %s", e, exc_info=True)
        await status_msg.edit_text(
            "❌ Произошла ошибка при поиске. Попробуйте позже.",
            parse_mode="HTML",
        )
        return

    await status_msg.delete()

    if not vacancies:
        no_results = (
            "😔 <b>Вакансии не найдены</b>\n\n"
            f"По словам {kw_preview} ничего не нашлось.\n\n"
            "<b>Советы:</b>\n"
            "• Попробуйте более общие слова\n"
            "• Проверьте правильность username каналов\n"
            "• Убедитесь, что вы авторизованы: <code>python auth.py</code>"
        )
        if failed:
            no_results += f"\n\n⚠️ <i>Недоступно: {', '.join('@' + c for c in failed)}</i>"
        await message.answer(no_results, reply_markup=search_results_kb(), parse_mode="HTML")
        return

    header = (
        f"✅ <b>Найдено: {len(vacancies)} вакансий</b>  •  "
        f"Каналов: {len(channels)}\n"
    )
    if failed:
        header += f"⚠️ Недоступно: {', '.join('@' + c for c in failed)}\n"
    header += "─" * 32

    await message.answer(header, parse_mode="HTML")

    for i, vacancy in enumerate(vacancies):
        try:
            await message.answer(
                vacancy.format_message(),
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
            if i < len(vacancies) - 1:
                await asyncio.sleep(0.3)
        except Exception as e:
            logger.warning("Не удалось отправить вакансию: %s", e)

    await message.answer(
        f"📋 Показано {len(vacancies)} вакансий.",
        reply_markup=search_results_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "search_again")
async def search_again(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    await callback.message.delete()
    # Создаём объект-заглушку с нужными полями
    msg = callback.message
    msg.from_user = callback.from_user
    await cmd_search(msg, bot)
