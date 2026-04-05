from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

import database as db
from keyboards import main_menu_kb

router = Router()

WELCOME_TEXT = """
👋 <b>Привет! Я бот для поиска вакансий в Telegram-каналах.</b>

Я умею:
• 🔍 Искать вакансии по ключевым словам в указанных каналах
• 🏷 Сохранять ваши ключевые слова
• 📢 Управлять списком каналов для поиска
• 🔔 Присылать уведомления о новых вакансиях

<b>Как начать:</b>
1. Добавьте ключевые слова → <i>🏷 Мои ключевые слова</i>
2. Добавьте каналы → <i>📢 Мои каналы</i>
3. Нажмите <i>🔍 Искать вакансии</i>

⚠️ <i>Бот должен быть участником каналов, которые вы добавляете, или каналы должны быть публичными.</i>
"""

HELP_TEXT = """
📖 <b>Справка</b>

<b>🔍 Поиск вакансий</b>
Запускает поиск по всем вашим каналам и ключевым словам. Показывает до 20 последних результатов.

<b>🏷 Ключевые слова</b>
Слова, по которым ищем вакансии. Например: <code>Python</code>, <code>удалённо</code>, <code>Senior</code>, <code>CAD</code>.
Поиск нечувствителен к регистру.

<b>📢 Каналы</b>
Список Telegram-каналов/групп для поиска. Добавляйте username без символа @.
Примеры: <code>it_vacancies</code>, <code>remote_jobs_ru</code>

<b>🔔 Уведомления</b>
При включении бот будет проверять каналы каждый час и присылать новые вакансии.

<b>⚙️ Технические детали</b>
Для чтения истории каналов используется Telethon (MTProto API).
Бот читает до 200 последних сообщений в каждом канале.

<b>Команды:</b>
/start — главное меню
/help — эта справка
/search — быстрый поиск
/keywords — управление ключевыми словами
/channels — управление каналами
"""


@router.message(CommandStart())
async def cmd_start(message: Message):
    db.upsert_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name,
    )
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_kb(), parse_mode="HTML")


@router.message(Command("help"))
@router.message(lambda m: m.text == "ℹ️ Помощь")
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT, parse_mode="HTML")
