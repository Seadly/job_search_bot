"""
telethon_searcher.py — поиск вакансий через Telethon (MTProto API).

Возможности:
- Поиск по ключевым словам в публичных каналах
- Кэширование результатов (TTL 10 минут)
- Отслеживание last_seen для уведомлений о новых вакансиях
"""

import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

API_ID   = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
PHONE    = os.getenv("PHONE", "")

# Кэш: channel -> (timestamp, messages)
_cache: dict[str, tuple[float, list]] = {}
CACHE_TTL = 600  # 10 минут

# last_seen[user_id][channel] = last_message_id
_last_seen: dict[int, dict[str, int]] = {}


@dataclass
class Vacancy:
    channel: str
    message_id: int
    text: str
    date: datetime
    url: str
    matched_keywords: list[str]

    def preview(self, max_len: int = 350) -> str:
        lines = [l.strip() for l in self.text.strip().splitlines() if l.strip()]
        preview = " • ".join(lines[:4])
        if len(preview) > max_len:
            preview = preview[:max_len] + "…"
        return preview

    def format_message(self) -> str:
        keywords_str = ", ".join(f"#{kw.replace(' ', '_')}" for kw in self.matched_keywords)
        date_str = self.date.strftime("%d.%m.%Y %H:%M")
        return (
            f"📌 <b>@{self.channel}</b>  •  <i>{date_str}</i>\n"
            f"🏷 {keywords_str}\n\n"
            f"{self.preview()}\n\n"
            f"🔗 <a href='{self.url}'>Открыть вакансию</a>"
        )


async def search_vacancies(
    channels: list[str],
    keywords: list[str],
    limit_per_channel: int = 200,
    max_results: int = 20,
    only_new: bool = False,
    user_id: Optional[int] = None,
) -> tuple[list[Vacancy], list[str]]:
    """
    Ищет вакансии по ключевым словам.

    Args:
        channels:           список username каналов (без @)
        keywords:           ключевые слова
        limit_per_channel:  сколько последних сообщений сканировать
        max_results:        максимум результатов
        only_new:           только новые (для уведомлений)
        user_id:            нужен при only_new=True

    Returns:
        (список Vacancy, список каналов с ошибками)
    """
    try:
        from telethon import TelegramClient
        from telethon.errors import (
            ChannelPrivateError, UsernameNotOccupiedError,
            FloodWaitError, ChatAdminRequiredError,
        )
    except ImportError:
        raise RuntimeError(
            "Установите telethon: pip install telethon\n"
            "Затем авторизуйтесь: python auth.py"
        )

    if not API_ID or not API_HASH:
        raise RuntimeError(
            "API_ID и API_HASH не заданы в .env!\n"
            "Получите их на https://my.telegram.org/apps"
        )

    results: list[Vacancy] = []
    failed: list[str] = []
    kw_lower = [kw.lower() for kw in keywords]

    async with TelegramClient("session_name", API_ID, API_HASH) as client:
        for channel in channels:
            if len(results) >= max_results:
                break
            try:
                messages = await _fetch_messages(client, channel, limit_per_channel)

                if only_new and user_id is not None:
                    last_id = _last_seen.get(user_id, {}).get(channel, 0)
                    messages = [m for m in messages if m["id"] > last_id]

                for msg in messages:
                    if not msg["text"]:
                        continue
                    matched = _matches(msg["text"], kw_lower)
                    if matched:
                        results.append(Vacancy(
                            channel=channel,
                            message_id=msg["id"],
                            text=msg["text"],
                            date=msg["date"],
                            url=f"https://t.me/{channel}/{msg['id']}",
                            matched_keywords=matched,
                        ))

                # Обновляем last_seen
                if only_new and user_id is not None and messages:
                    if user_id not in _last_seen:
                        _last_seen[user_id] = {}
                    _last_seen[user_id][channel] = max(m["id"] for m in messages)

            except FloodWaitError as e:
                logger.warning("FloodWait %ds для @%s", e.seconds, channel)
                failed.append(channel)
            except (ChannelPrivateError, UsernameNotOccupiedError, ChatAdminRequiredError) as e:
                logger.warning("Канал @%s недоступен: %s", channel, e)
                failed.append(channel)
            except Exception as e:
                logger.error("Ошибка @%s: %s", channel, e, exc_info=True)
                failed.append(channel)

    results.sort(key=lambda v: v.date, reverse=True)
    return results[:max_results], failed


async def _fetch_messages(client, channel: str, limit: int) -> list[dict]:
    """Получает сообщения из канала с кэшированием."""
    now = time.time()
    cached = _cache.get(channel)
    if cached and (now - cached[0]) < CACHE_TTL:
        logger.debug("Кэш @%s (возраст %.0fs)", channel, now - cached[0])
        return cached[1]

    logger.info("Загружаю @%s (limit=%d)...", channel, limit)
    entity = await client.get_entity(f"@{channel}")

    messages = []
    async for msg in client.iter_messages(entity, limit=limit):
        text = msg.text or getattr(msg, "message", "") or ""
        if text:
            messages.append({
                "id":   msg.id,
                "text": text,
                "date": msg.date.replace(tzinfo=None),
            })

    _cache[channel] = (now, messages)
    logger.info("  → %d сообщений из @%s", len(messages), channel)
    return messages


def _matches(text: str, keywords: list[str]) -> list[str]:
    t = text.lower()
    return [kw for kw in keywords if kw in t]


def clear_cache():
    _cache.clear()
    logger.info("Кэш очищен")
