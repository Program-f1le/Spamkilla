import asyncio
from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from config import BOT_TOKEN, CHANNEL_ID, ADM_GROUP_ID
from handlers.admin import admin_router
from handlers.channel import channel_router
from db.engine import engine
from db.models import Base


async def check_bot_permissions(bot: Bot) -> bool:
    """Проверяет права бота в группе обсуждений и в админ-чате при старте."""
    # Явно получаем данные бота — кешируется в aiogram автоматически
    bot_info = await bot.get_me()

    print("\n" + "=" * 50)
    print(f"🔍 Проверка прав бота @{bot_info.username} (ID: {bot_info.id})")
    print("=" * 50)

    all_ok = True

    for chat_id, label in [(CHANNEL_ID, "Группа обсуждений"), (ADM_GROUP_ID, "Админ-чат")]:
        print(f"\n📌 {label} (ID: {chat_id})")
        try:
            # Получаем информацию о боте как участнике чата
            member = await bot.get_chat_member(chat_id=chat_id, user_id=bot_info.id)
            status = member.status

            if status in ("left", "kicked"):
                print(f"  ❌ Бот НЕ является участником чата! (статус: {status})")
                all_ok = False
                continue

            print(f"  ✅ Бот в чате (статус: {status})")

            # Проверяем нужные права (только для группы обсуждений)
            if chat_id == CHANNEL_ID:
                if status == "administrator":
                    # Явно приводим к bool: None → False, True → True
                    can_delete = bool(member.can_delete_messages)
                    can_ban = bool(member.can_restrict_members)
                    print(f"  {'✅' if can_delete else '❌'} Право удалять сообщения: {can_delete}")
                    print(f"  {'✅' if can_ban else '❌'} Право банить пользователей: {can_ban}")
                    if not can_delete or not can_ban:
                        print("  ⚠️  Боту нужны оба права для работы в normal-режиме!")
                        all_ok = False
                else:
                    print("  ❌ Бот НЕ является администратором!")
                    print("  ⚠️  Без прав администратора бот работает в Privacy Mode")
                    print("  ⚠️  и НЕ видит сообщения пользователей!")
                    all_ok = False

        except TelegramForbiddenError:
            print("  ❌ Бот заблокирован или не имеет доступа к чату!")
            all_ok = False
        except TelegramBadRequest as e:
            print(f"  ❌ Ошибка запроса: {e}")
            all_ok = False
        except Exception as e:
            print(f"  ❌ Неожиданная ошибка: {type(e).__name__}: {e}")
            all_ok = False

    print("\n" + "=" * 50)
    if all_ok:
        print("✅ Все проверки пройдены — бот готов к работе!")
    else:
        print("⚠️  Есть проблемы с правами! Бот запущен, но может работать некорректно.")
    print("=" * 50 + "\n")

    return all_ok


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Создаем таблицы в БД при запуске (так как нет миграций Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Проверяем права бота перед запуском
    await check_bot_permissions(bot)

    # Подключаем роутеры (важен порядок: сначала админский)
    dp.include_router(admin_router)
    dp.include_router(channel_router)

    print("Бот запущен...")
    # Запускаем получение обновлений
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())