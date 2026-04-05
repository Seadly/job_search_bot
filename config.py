import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в .env файле!")

# Список публичных Telegram-каналов/групп с вакансиями для парсинга
# Добавьте username каналов (без @) куда у бота есть доступ
DEFAULT_CHANNELS = [
    "it_vacancies",          # пример — замените реальными каналами
    "remote_jobs_ru",
    "jobs_for_designers",
    "python_jobs_ru",
]

# Максимум сообщений для поиска в одном канале
MAX_MESSAGES_PER_CHANNEL = 200

# Максимум результатов в одном ответе
MAX_RESULTS = 20
