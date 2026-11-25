from collections.abc import Iterator
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.engine import Engine


def create_database_engine(database_path: Path | str) -> Engine:
    path = Path(database_path)
    if str(database_path) != ":memory:":
        path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )


def create_db_and_tables(engine: Engine) -> None:
    SQLModel.metadata.create_all(engine)


def get_session(engine: Engine) -> Iterator[Session]:
    with Session(engine) as session:
        yield session
