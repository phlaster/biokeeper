from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

from config import database_url


engine = create_engine(database_url,
                        # echo=True,
                        pool_size=5,
                        max_overflow=20)

SessionLocal = sessionmaker(engine, expire_on_commit=False, autocommit=False, autoflush=False)