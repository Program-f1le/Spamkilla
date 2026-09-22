from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject, Message, CallbackQuery
from config import ADM_GROUP_ID

class IsAdminChat(BaseFilter):
    async def __call__(self, event: TelegramObject) -> bool:
        if isinstance(event, CallbackQuery):
            return event.message.chat.id == ADM_GROUP_ID
        if isinstance(event, Message):
            return event.chat.id == ADM_GROUP_ID
        return False