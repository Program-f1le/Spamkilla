from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL_ID, ADM_GROUP_ID
import handlers.admin # Для доступа к BOT_MODE
from services import check_message_for_spam
from db.requests import is_whitelisted, add_ban_log

channel_router = Router()

# === ДИАГНОСТИКА: логируем ВСЕ входящие сообщения ===
@channel_router.message(F.text)
async def debug_all_messages(message: Message):
    print(f"[DEBUG] chat.id={message.chat.id} | chat.type={message.chat.type} | text={message.text[:30]!r}")
    print(f"[DEBUG] CHANNEL_ID из конфига = {CHANNEL_ID}")
    if message.chat.id == CHANNEL_ID:
        await moderate_message(message)

# Основной обработчик (вызывается из debug или напрямую через channel_post)
@channel_router.channel_post(F.chat.id == CHANNEL_ID, F.text)
async def moderate_message(message: Message):
    # Добавляем принт для отладки. Если в консоли это не появится — 
    # значит сообщение перехватывается другим роутером (ищи мусор в admin.py)
    print(f"👀 Проверяю сообщение в канале: {message.text[:20]}...")

    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    
    # 1. Проверка вайтлиста через БД
    if await is_whitelisted(user_id):
        print(f"⚪️ Пользователь {user_id} в белом списке. Пропускаю.")
        return

    # 3. Отправка в нейросеть
    verdict = await check_message_for_spam(message.text)
    print(f"🤖 Вердикт нейросети: {verdict}")

    # 4. Обработка вердикта
    if verdict.get("is_spam"):
        if handlers.admin.BOT_MODE == "test":
            # Тестовый режим: отправка админам на проверку
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Забанить", callback_data=f"ban_{user_id}_{message.chat.id}_{message.message_id}"),
                    InlineKeyboardButton(text="Пропустить", callback_data="skip")
                ]
            ])
            await message.bot.send_message(
                ADM_GROUP_ID,
                f"⚠️ Подозрение на спам!\nID: {user_id}\nТекст: {message.text}",
                reply_markup=kb
            )
        else:
            # Обычный режим: сразу удаляем и баним
            await message.delete()
            try:
                await message.chat.ban(user_id)
            except Exception as e:
                print(f"Не удалось забанить {user_id}: {e}")
            
            await add_ban_log(user_id, message.text)
            await message.bot.send_message(
                ADM_GROUP_ID,
                f"✅ Забанен спамер!\nID: {user_id}\nТекст: {message.text}"
            )