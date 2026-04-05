# 🤖 Telegram Job Search Bot

Бот для поиска вакансий в Telegram-каналах по ключевым словам.

## 📋 Возможности

- 🔍 Поиск вакансий по ключевым словам в любых публичных каналах
- 🏷 Сохранение персональных ключевых слов
- 📢 Управление списком каналов для мониторинга
- 🔔 Автоматические уведомления о новых вакансиях (каждый час)
- 💾 SQLite база данных для хранения настроек

## 🗂 Структура проекта

```
job_search_bot/
├── bot.py                  # Точка входа, запуск бота
├── config.py               # Конфигурация и настройки
├── database.py             # Работа с SQLite
├── telethon_searcher.py    # Поиск через Telethon (MTProto)
├── keyboards.py            # Клавиатуры и кнопки
├── handlers/
│   ├── __init__.py         # Регистрация роутеров
│   ├── start.py            # /start, /help
│   ├── keywords.py         # Управление ключевыми словами
│   ├── channels.py         # Управление каналами
│   ├── search.py           # Запуск поиска
│   └── alerts.py           # Уведомления и планировщик
├── .env.example            # Пример переменных окружения
├── requirements.txt
└── README.md
```

## ⚙️ Установка

### 1. Клонировать / скопировать проект

```bash
cd job_search_bot
```

### 2. Создать виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate       # Linux / macOS
venv\Scripts\activate          # Windows
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Получить токены

#### 4.1 Токен бота (от @BotFather)
1. Откройте @BotFather в Telegram
2. Напишите `/newbot`
3. Следуйте инструкциям, получите токен вида `1234567890:ABC...`

#### 4.2 API_ID и API_HASH (для Telethon)
> Нужны для чтения истории каналов через MTProto

1. Перейдите на https://my.telegram.org
2. Войдите через номер телефона
3. Выберите **"API development tools"**
4. Создайте приложение, получите `api_id` и `api_hash`

### 5. Настроить .env

```bash
cp .env.example .env
```

Откройте `.env` и заполните:

```env
BOT_TOKEN=ваш_токен_от_botfather
API_ID=ваш_api_id
API_HASH=ваш_api_hash
PHONE=+79001234567
```

### 6. Первая авторизация Telethon

При первом запуске Telethon попросит подтвердить номер телефона:

```bash
python -c "
import asyncio
from telethon import TelegramClient
from config import API_ID, API_HASH
import os; from dotenv import load_dotenv; load_dotenv()

async def auth():
    async with TelegramClient('session_name', API_ID, API_HASH) as c:
        print('Авторизация успешна:', await c.get_me())

asyncio.run(auth())
"
```

Введите код из Telegram. После этого создастся файл `session_name.session` — он сохраняет сессию.

### 7. Запуск бота

```bash
python bot.py
```

## 🚀 Деплой на сервер

### Вариант 1 — systemd (рекомендуется для VPS)

Создайте файл `/etc/systemd/system/jobbot.service`:

```ini
[Unit]
Description=Telegram Job Search Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/job_search_bot
ExecStart=/home/ubuntu/job_search_bot/venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable jobbot
sudo systemctl start jobbot
sudo systemctl status jobbot
```

### Вариант 2 — Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

```bash
docker build -t jobbot .
docker run -d --env-file .env --name jobbot jobbot
```

### Вариант 3 — Railway / Render (бесплатно)
1. Залейте код на GitHub (не забудьте добавить `.env` в `.gitignore`!)
2. Подключите репозиторий к Railway/Render
3. Укажите переменные окружения в настройках сервиса

## 📢 Рекомендуемые каналы с вакансиями

| Тематика | Username |
|----------|---------|
| IT вакансии | `it_vacancies` |
| Удалённая работа | `remote_jobs_ru` |
| Python | `python_jobs_ru` |
| Дизайн | `jobs_for_designers` |
| Инженерные вакансии | `engineer_jobs_ru` |
| CAD / Mechanical | `cad_jobs` |

> ⚠️ Проверяйте актуальность username — каналы могут менять названия.

## 🔒 Безопасность

- Никогда не коммитьте `.env` в Git
- Добавьте в `.gitignore`:
  ```
  .env
  *.session
  job_bot.db
  ```

## 📝 Лицензия

MIT
