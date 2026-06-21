from sqlalchemy.ext.asyncio import async_sessionmaker,AsyncSession,create_async_engine
from sqlalchemy.orm import declarative_base


ASYNC_DATABASE_URL = "mysql+aiomysql://username:password@ip:port/database_name?charset=utf8mb4"


async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo = True,
    pool_size = 10,
    max_overflow = 20
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()