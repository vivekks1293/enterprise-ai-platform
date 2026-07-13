from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config.settings import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)