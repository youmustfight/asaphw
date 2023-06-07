import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import env

# ENGINE/BiND
_sqlalchemy_engine = create_async_engine(env.env_get_database_app_url())

# SESSION MAKER
_sqlalchemy_sessionmaker = sessionmaker(
    _sqlalchemy_engine,
    AsyncSession,
    expire_on_commit=False,
    future=True,
)

def create_sqlalchemy_session():
    return _sqlalchemy_sessionmaker()