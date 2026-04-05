import asyncio
import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

import database as db
from keyboards import alerts_kb

router = Router()
logger = logging.getLogger(__name__)

CHECK_INTERVAL = 3600  # 1 час


def alerts_text(enabled: bool) -> str:
    status = "🔔 <b>включены</b>" if enabled else "🔕 <b>выключены</b>"
    return (
        f"🔔 <b>Уведомления о новых вакансиях</b>\n\n"
        f"Статус: {status}\n\n"
        "При включённых уведомлениях бот проверяет ваши каналы "
        "каждый час и присылает только <b>новые</b> вакансии, "
        "которые ещё не попадались вам ранее."
    )


@router.message(Command("alerts"))
@router.message(F.text == "🔔 Уведомления")
async def show_alerts(message: Message):
    enabled = db.get_alerts_enabled(message.from_user.id)
    await message.answer(alerts_text(enabled), reply_markup=alerts_kb(enabled), parse_mode="HTML")


@router.callback_query(F.data.in_({"alerts_on", "alerts_off"}))
async def toggle_alerts(callback: CallbackQuery):
    enabled = callback.data == "alerts_on"
    db.set_alerts(callback.from_user.id, enabled)
    await callback.message.edit_text(
        alerts_text(enabled),
        reply_markup=alerts_kb(enabled),
        parse_mode="HTML",
    )
    await callback.answer("Включены ✅" if enabled else "Выключены ❌")


async def alerts_scheduler(bot: Bot):
    """Фоновая задача: каждый час проверяет новые вакансии для подписчиков."""
    from telethon_searcher import search_vacancies

    logger.info("Планировщик уведомлений запущен (интервал: %dс)", CHECK_INTERVAL)
    await asyncio.sleep(30)  # небольшая задержка после старта

    while True:
        user_ids = db.get_all_alert_users()
        if user_ids:
            logger.info("Проверка уведомлений для %d пользователей...", len(user_ids))

        for user_id in user_ids:
            try:
                keywords = db.get_keywords(user_id)
                channels = db.get_channels(user_id)
                if not keywords or not channels:
                    continue

                vacancies, failed = await search_vacancies(
                    channels=channels,
                    keywords=keywords,
                    limit_per_channel=50,
                    max_results=10,
                    only_new=True,
                    user_id=user_id,
                )

                if not vacancies:
                    continue

                await bot.send_message(
                    user_id,
                    f"🔔 <b>Новые вакансии по вашим запросам!</b>\n"
                    f"Найдено: {len(vacancies)} шт.",
                    parse_mode="HTML",
                )

                for vacancy in vacancies:
                    try:
                        await bot.send_message(
                            user_id,
                            vacancy.format_message(),
                            parse_mode="HTML",
                            disable_web_page_preview=True,
                        )
                        await asyncio.sleep(0.3)
                    except Exception as e:
                        logger.warning("Не удалось отправить вакансию: %s", e)

                if failed:
                    await bot.send_message(
                        user_id,
                        f"⚠️ <i>Недоступные каналы: {', '.join('@' + c for c in failed)}</i>",
                        parse_mode="HTML",
                    )

            except Exception as e:
                logger.error("Ошибка уведомления user %d: %s", user_id, e)

        await asyncio.sleep(CHECK_INTERVAL)
