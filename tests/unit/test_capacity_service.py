from datetime import date
from io import StringIO

import pytest
from sqlmodel import Session, select

from cathotel.database import create_database_engine, create_db_and_tables
from cathotel.models import CapacityDate
from cathotel.services.capacity import CapacityImportError, import_capacity_csv


@pytest.fixture

def session(tmp_path):
    engine = create_database_engine(tmp_path / "capacity.sqlite")
    create_db_and_tables(engine)
    with Session(engine) as db_session:
        yield db_session


def test_import_parses_iso_dates_and_nonnegative_whole_capacities(session):
    result = import_capacity_csv(
        session,
        StringIO("date,room_capacity\n2030-01-01,8\n2030-01-02,0\n"),
    )

    assert result == 2
    rows = session.exec(select(CapacityDate).order_by(CapacityDate.date)).all()
    assert [(row.date, row.room_capacity) for row in rows] == [
        (date(2030, 1, 1), 8),
        (date(2030, 1, 2), 0),
    ]


@pytest.mark.parametrize(
    "csv_text",
    [
        "date,capacity\n2030-01-01,8\n",
        "date,room_capacity\nnot-a-date,8\n",
        "date,room_capacity\n2030-01-01,-1\n",
        "date,room_capacity\n2030-01-01,1.5\n",
        "date,room_capacity\n2030-01-01,one\n",
        "date,room_capacity\n2030-01-01,8\n2030-01-01,9\n",
        "date,room_capacity\n2030-01-01,8,extra\n",
    ],
)
def test_invalid_csv_is_rejected_without_partial_updates(session, csv_text):
    import_capacity_csv(
        session, StringIO("date,room_capacity\n2030-02-01,3\n")
    )
    before = session.exec(select(CapacityDate).order_by(CapacityDate.date)).all()

    with pytest.raises(CapacityImportError):
        import_capacity_csv(session, StringIO(csv_text))

    after = session.exec(select(CapacityDate).order_by(CapacityDate.date)).all()
    assert [(row.date, row.room_capacity) for row in after] == [
        (row.date, row.room_capacity) for row in before
    ]


def test_import_updates_listed_dates_and_leaves_omitted_dates_unchanged(session):
    import_capacity_csv(
        session,
        StringIO("date,room_capacity\n2030-01-01,8\n2030-01-02,6\n"),
    )

    import_capacity_csv(
        session,
        StringIO("date,room_capacity\n2030-01-01,9\n"),
    )

    rows = session.exec(select(CapacityDate).order_by(CapacityDate.date)).all()
    assert [(row.date, row.room_capacity) for row in rows] == [
        (date(2030, 1, 1), 9),
        (date(2030, 1, 2), 6),
    ]
