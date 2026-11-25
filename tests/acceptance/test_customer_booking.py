from datetime import date, timedelta
from pathlib import Path

from sqlmodel import Session, select
from streamlit.testing.v1 import AppTest

from cathotel.config import get_settings
from cathotel.database import create_database_engine, create_db_and_tables
from cathotel.models import CapacityDate, Reservation

APP_PATH = Path(__file__).parents[2] / "src" / "cathotel" / "web.py"


def test_customer_can_open_booking_page_with_no_past_date_selection(tmp_path, monkeypatch):
    database_path = tmp_path / "customer.sqlite"
    engine = create_database_engine(database_path)
    create_db_and_tables(engine)
    arrival = date.today() + timedelta(days=1)
    with Session(engine) as session:
        session.add_all(
            [
                CapacityDate(date=arrival, room_capacity=2),
                CapacityDate(date=arrival + timedelta(days=1), room_capacity=2),
            ]
        )
        session.commit()

    monkeypatch.setenv("DATABASE_PATH", str(database_path))
    monkeypatch.setenv("HOTEL_TIMEZONE", "UTC")
    get_settings.cache_clear()
    at = AppTest.from_file(str(APP_PATH), default_timeout=10).run()

    assert not at.exception
    assert not any("staff" in button.label.lower() for button in at.button)
    assert all(widget.min >= date.today() for widget in at.date_input)
    at.date_input[0].set_value(arrival).run()
    at.date_input[1].set_value(arrival + timedelta(days=1)).run()
    at.button[0].click().run()
    assert not at.exception
    assert any("available" in item.value.lower() for item in at.success)
    assert len(at.text_input) == 2
    at.text_input[0].set_value("Mimi")
    at.text_input[1].set_value("Tabby")
    at.button[1].click().run()
    assert not at.exception
    assert any("confirmed" in item.value.lower() for item in at.success)
    assert any("Reservation code: " in item.value for item in at.subheader)
    with Session(engine) as session:
        reservation = session.exec(select(Reservation)).one()
    assert reservation.arrival_date == arrival
    assert reservation.departure_date == arrival + timedelta(days=1)
