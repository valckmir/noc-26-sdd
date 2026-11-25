from datetime import date, timedelta
from pathlib import Path

from sqlmodel import Session, select
from streamlit.testing.v1 import AppTest

from cathotel.config import get_settings
from cathotel.database import create_database_engine, create_db_and_tables
from cathotel.models import CapacityDate, Reservation, ReservationStatus

APP_PATH = Path(__file__).parents[2] / "src" / "cathotel" / "web.py"


def test_customer_can_lookup_and_cancel_reservation_by_code(tmp_path, monkeypatch):
    database_path = tmp_path / "manage.sqlite"
    engine = create_database_engine(database_path)
    create_db_and_tables(engine)
    check_in = date.today() + timedelta(days=3)
    with Session(engine) as session:
        session.add_all(
            [
                CapacityDate(date=check_in, room_capacity=2),
                CapacityDate(date=check_in + timedelta(days=1), room_capacity=2),
            ]
        )
        session.add(
            Reservation(
                code="012345",
                arrival_date=check_in,
                departure_date=check_in + timedelta(days=2),
                cat_name="Mimi",
                breed="Tabby",
                is_social=True,
                daily_walks_required=False,
            )
        )
        session.commit()

    monkeypatch.setenv("DATABASE_PATH", str(database_path))
    monkeypatch.setenv("HOTEL_TIMEZONE", "UTC")
    get_settings.cache_clear()
    at = AppTest.from_file(str(APP_PATH), default_timeout=10).run()

    assert not at.exception
    at.radio[0].set_value("Manage reservation").run()
    assert len(at.text_input) == 1
    at.text_input[0].set_value("012-345")
    at.button[0].click().run()
    assert not at.exception
    assert any("Mimi" in item.value for item in at.markdown)
    assert len(at.button) == 2
    at.button[1].click().run()
    assert not at.exception
    with Session(engine) as session:
        reservation = session.exec(select(Reservation)).one()
    assert reservation.status == ReservationStatus.ACTIVE
    assert any("sure you want to cancel" in item.value.lower() for item in at.warning)
    assert len(at.button) == 3
    assert [button.label for button in at.button] == [
        "Find reservation",
        "Confirm cancellation",
        "Keep reservation",
    ]
    at.button[1].click().run()
    assert not at.exception
    assert any("cancelled" in item.value.lower() for item in at.success)
    with Session(engine) as session:
        reservation = session.exec(select(Reservation)).one()
    assert reservation.status == ReservationStatus.CANCELLED
