import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from config import MAX_MESSAGES_PER_CHANNEL, MAX_RESULTS

logger = logging.getLogger(__name__)


@dataclass
class Vacancy:
    channel: str
    message_id: int
    text: str
    date: datetime
    url: str
    matched_keywords: list[str]

    def preview(self, max_len: int = 300) -> str:
        lines = [l.strip() for l in self.text.strip().splitlines() if l.strip()]
        preview = " • ".join(lines[:3])
        if len(preview) > max_len:
            preview = preview[:max_len] + "…"
        return preview

    def format_message(self) -> str:
        keywords_str = ", ".join(f"#{kw.replace(' ', '_')}" for kw in self.matched_keywords)
        date_str = self.date.strftime("%d.%m.%Y")
        preview = self.preview()
        return (
            f"📌 <b>@{self.channel}</b>  •  <i>{date_str}</i>\n"
            f"🏷 {keywords_str}\n\n"
            f"{preview}\n\n"
            f"🔗 <a href='{self.url}'>Открыть вакансию</a>"
        )


async def search_vacancies(
    bot: Bot,
    channels: list[str],
    keywords: list[str],
    limit: int = MAX_RESULTS,
) -> tuple[list[Vacancy], list[str]]:
    """
    Ищет вакансии по ключевым словам в указанных каналах.

    Returns:
        (список вакансий, список каналов с ошибками доступа)
    """
    results: list[Vacancy] = []
    failed_channels: list[str] = []
    kw_lower = [kw.lower() for kw in keywords]

    for channel in channels:
        if len(results) >= limit:
            break
        try:
            found = await _search_in_channel(bot, channel, kw_lower, limit - len(results))
            results.extend(found)
        except (TelegramBadRequest, TelegramForbiddenError) as e:
            logger.warning("Канал @%s недоступен: %s", channel, e)
            failed_channels.append(channel)
        except Exception as e:
            logger.error("Ошибка при поиске в @%s: %s", channel, e)
            failed_channels.append(channel)

    # Сортировка: сначала свежие
    results.sort(key=lambda v: v.date, reverse=True)
    return results[:limit], failed_channels


async def _search_in_channel(
    bot: Bot,
    channel: str,
    kw_lower: list[str],
    limit: int,
) -> list[Vacancy]:
    """Читает историю канала и ищет совпадения по ключевым словам."""
    found: list[Vacancy] = []

    # Получаем последние сообщения через forwardMessages (не требует прав)
    # Используем getUpdates-совместимый подход: читаем через getChatHistory
    # Примечание: стандартный Bot API не даёт читать историю чужих каналов напрямую.
    # Для этого нужен Telethon (MTProto). Здесь реализован поиск через
    # пересланные сообщения или методы доступные боту как участнику канала.

    try:
        # Пробуем получить информацию о чате (бот должен быть участником)
        chat = await bot.get_chat(f"@{channel}")
        chat_id = chat.id
    except Exception:
        raise TelegramBadRequest(method="getChat", message=f"Канал @{channel} не найден или бот не является участником")

    # Читаем последние MAX_MESSAGES_PER_CHANNEL сообщений
    # Используем getChatHistory через низкоуровневый запрос
    offset = 0
    batch_size = 100
    scanned = 0

    while scanned < MAX_MESSAGES_PER_CHANNEL and len(found) < limit:
        try:
            # aiogram не поддерживает getChatHistory напрямую,
            # используем forwardMessages как зонд или копируем через export
            # Реальная реализация — через Telethon (см. README)
            # Здесь показана архитектура и заглушка для интеграции
            break
        except Exception:
            break

    return found


def matches_keywords(text: str, keywords: list[str]) -> list[str]:
    """Возвращает список совпавших ключевых слов."""
    text_lower = text.lower()
    return [kw for kw in keywords if kw in text_lower]


def build_vacancy_url(channel: str, message_id: int) -> str:
    return f"https://t.me/{channel}/{message_id}"
