from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from filters import IsAdminChat
from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.filters import CommandObject
from db.requests import add_ban_log, add_whitelist, remove_whitelist, remove_ban_log, get_bans_count, get_whitelist
from config import CHANNEL_ID

admin_router = Router()
# Применяем фильтр ко всему роутеру: команды сработают только в админ-чате
admin_router.message.filter(IsAdminChat())
admin_router.callback_query.filter(IsAdminChat())

# Локальная переменная для режима (как договорились)
BOT_MODE = "test" 

@admin_router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "Доступные команды:\n"
        "/mode — переключить режим (test/normal)\n"
        "/whitelist add <id> — добавить в белый список\n"
        "/whitelist remove <id> — удалить из белого списка\n"
        "/whitelist list — показать белый список\n"
        "/unban <id> — разбанить пользователя\n"
        "/stats — статистика банов\n"
        f"Текущий режим: {BOT_MODE}"
    )
    await message.answer(text)

@admin_router.message(Command("mode"))
async def cmd_mode(message: Message):
    global BOT_MODE
    BOT_MODE = "test" if BOT_MODE == "normal" else "normal"
    await message.answer(f"Режим бота изменен на: {BOT_MODE}")

@admin_router.message(Command("whitelist"))
async def cmd_whitelist(message: Message, command: CommandObject):
    if not command.args:
        return await message.answer("Формат: /whitelist add <id>, /whitelist remove <id> или /whitelist list")
    
    args = command.args.split()
    action = args[0]
    
    if action == "list":
        users = await get_whitelist()
        if not users:
            return await message.answer("⚪️ Белый список пуст.")
        return await message.answer("⚪️ <b>Белый список:</b>\n" + "\n".join([str(u) for u in users]), parse_mode="HTML")
    
    if len(args) != 2 or not args[1].isdigit():
        return await message.answer("Ошибка! Формат: /whitelist add 123456")
    
    user_id = int(args[1])
    
    if action == "add":
        await add_whitelist(user_id)
        await message.answer(f"✅ Пользователь {user_id} добавлен в белый список.")
    elif action == "remove":
        await remove_whitelist(user_id)
        await message.answer(f"✅ Пользователь {user_id} удален из белого списка.")

@admin_router.message(Command("unban"))
async def cmd_unban(message: Message, command: CommandObject):
    if not command.args or not command.args.isdigit():
        return await message.answer("Формат: /unban <id>")
    
    user_id = int(command.args)
    
    try:
        # Снимаем бан в самом канале (нужен config.CHANNEL_ID)
        await message.bot.unban_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        # Удаляем из БД
        await remove_ban_log(user_id)
        await message.answer(f"✅ Пользователь {user_id} разбанен, запись удалена из лога.")
    except Exception as e:
        await message.answer(f"❌ Ошибка разбана: {e}")

@admin_router.message(Command("stats"))
async def cmd_stats(message: Message):
    count = await get_bans_count()
    await message.answer(f"📊 <b>Статистика модерации:</b>\nВсего забанено: {count}", parse_mode="HTML")

@admin_router.callback_query(F.data.startswith("ban_"))
async def cb_ban(callback: CallbackQuery):
    # maxsplit=3 защищает от лишних разбивок, если в callback_data есть '_'
    _, user_id, chat_id, msg_id = callback.data.split("_", maxsplit=3)
    user_id, chat_id, msg_id = int(user_id), int(chat_id), int(msg_id)
    
    try:
        # Удаляем сообщение из канала и баним
        await callback.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        await callback.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        
        # Извлекаем текст из сообщения админ-чата для БД
        msg_text = callback.message.text.split("Текст: ")[-1]
        await add_ban_log(user_id, msg_text)
        
        await callback.message.edit_text(f"✅ Ручной бан выдан.\nID: {user_id}\nТекст: {msg_text}")
    except Exception as e:
        await callback.answer(f"Ошибка: {e}", show_alert=True)

@admin_router.callback_query(F.data == "skip")
async def cb_skip(callback: CallbackQuery):
    await callback.message.edit_text(callback.message.text + "\n\n*Пропущено администратором*")