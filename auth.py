"""
auth.py — одноразовая авторизация Telethon.

Запустите ОДИН РАЗ перед стартом бота:
    python auth.py

После успешной авторизации создастся файл session_name.session.
Больше запускать не нужно — сессия сохраняется автоматически.
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

API_ID   = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
PHONE    = os.getenv("PHONE", "")


async def main():
    try:
        from telethon import TelegramClient
    except ImportError:
        print("❌ Установите telethon: pip install telethon")
        return

    if not API_ID or not API_HASH:
        print("❌ API_ID и API_HASH не заданы в .env файле!")
        print("   Получите их на https://my.telegram.org/apps")
        return

    print("🔐 Авторизация Telethon...")
    print(f"   API_ID:  {API_ID}")
    print(f"   PHONE:   {PHONE or '(будет запрошен)'}")
    print()

    async with TelegramClient("session_name", API_ID, API_HASH) as client:
        if not PHONE:
            phone = input("Введите номер телефона (формат +79001234567): ").strip()
        else:
            phone = PHONE

        await client.start(phone=phone)
        me = await client.get_me()
        print(f"\n✅ Авторизация успешна!")
        print(f"   Имя:     {me.first_name} {me.last_name or ''}")
        print(f"   Username: @{me.username or 'нет'}")
        print(f"   ID:      {me.id}")
        print(f"\n📁 Сессия сохранена в session_name.session")
        print("   Теперь можно запускать бота: python bot.py")

        # Тест: проверяем доступ к публичному каналу
        print("\n🔍 Тест доступа к каналам...")
        try:
            entity = await client.get_entity("telegram")
            print(f"   ✅ Тест пройден — канал @telegram доступен")
        except Exception as e:
            print(f"   ⚠️  Тест не прошёл: {e}")


if __name__ == "__main__":
    asyncio.run(main())
