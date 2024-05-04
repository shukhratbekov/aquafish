from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from configs import PG_NAME, PG_HOST, PG_PORT, PG_USER, PG_PASSWORD

engine = create_async_engine(f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_NAME}")

async_session = async_sessionmaker(bind=engine)

Base = declarative_base()


