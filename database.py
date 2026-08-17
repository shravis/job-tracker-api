from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()


def get_env_variable(name: str) -> str:
    value = os.getenv(name)

    if value is None:
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value


DATABASE_URL = get_env_variable("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()