import sqlalchemy
from cashews import Cache
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from app.db.asyncpg_utils import *  # noqa
from config import settings_app
from config import settings_redis

DATABASE_URL = settings_app.dsn

engine = create_async_engine(
    DATABASE_URL,
    future=True,
    echo=False,
    connect_args={"timeout": 30},
    pool_size=200,
    max_overflow=300,
)

sync_engine = create_engine(settings_app.sync_dns)

async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
autocommit_engine = engine.execution_options(isolation_level="AUTOCOMMIT")

metadata = sqlalchemy.MetaData()
Base = declarative_base(metadata=metadata)

cache = Cache()
cache.setup(
    settings_url=settings_redis.dsn(
        host=settings_redis.REDIS_HOST,
        port=settings_redis.REDIS_PORT,
        user=settings_redis.REDIS_USER,
        password=settings_redis.REDIS_PWD,
        database=settings_redis.REDIS_DB,
    ),
    client_side=True,
    retry_on_timeout=True,
    hash_key="1337",
)
