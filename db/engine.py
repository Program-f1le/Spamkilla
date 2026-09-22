from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from asyncio import run
from config import DB_URL

engine = create_async_engine(DB_URL, echo=False)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
