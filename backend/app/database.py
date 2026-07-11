from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import pathlib

# Ensure the data directory exists (works locally and in Docker)
_db_dir = pathlib.Path(__file__).resolve().parent / "data"
_db_dir.mkdir(parents=True, exist_ok=True)
_db_path = _db_dir / "hwt_blog.db"

DATABASE_URL = f"sqlite:///{_db_path.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30,
    },
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
