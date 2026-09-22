from sqlalchemy import select, delete, func
from db.engine import async_session_maker
from db.models import Whitelist, BansLog

async def is_whitelisted(user_id: int) -> bool:
    async with async_session_maker() as session:
        result = await session.execute(select(Whitelist).where(Whitelist.user_id == user_id))
        return result.scalar_one_or_none() is not None

async def add_ban_log(user_id: int, message_text: str):
    async with async_session_maker() as session:
        session.add(BansLog(user_id=user_id, message=message_text))
        await session.commit()

async def add_whitelist(user_id: int):
    async with async_session_maker() as session:
        session.add(Whitelist(user_id=user_id))
        await session.commit()

async def remove_whitelist(user_id: int):
    async with async_session_maker() as session:
        await session.execute(delete(Whitelist).where(Whitelist.user_id == user_id))
        await session.commit()

async def remove_ban_log(user_id: int):
    async with async_session_maker() as session:
        await session.execute(delete(BansLog).where(BansLog.user_id == user_id))
        await session.commit()

async def get_bans_count() -> int:
    async with async_session_maker() as session:
        result = await session.execute(select(func.count()).select_from(BansLog))
        return result.scalar()

async def get_whitelist() -> list[int]:
    async with async_session_maker() as session:
        result = await session.execute(select(Whitelist.user_id))
        return result.scalars().all()