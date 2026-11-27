from datetime import date, timedelta
from pathlib import Path

from sqlmodel import Session, select
from streamlit.testing.v1 import AppTest

from cathotel.config import get_settings
from cathotel.database import create_database_engine, create_db_and_tables
from cathotel.models import Feedback, Reservation

APP_PATH = Path(__file__).parents[2] / "src" / "cathotel" / "web.py"


def setup_app(tmp_path, monkeypatch, arrival, departure, feedback_rating=None):
    database_path = tmp_path / "feedback.sqlite"
    engine = create_database_engine(database_path)
    create_db_and_tables(engine)
    with Session(engine) as session:
        reservation = Reservation(
            code="012345",
            arrival_date=arrival,
            departure_date=departure,
            cat_name="Mimi",
            breed="Tabby",
            is_social=True,
            daily_walks_required=False,
        )
        session.add(reservation)
        session.commit()
        if feedback_rating is not None:
            session.add(
                Feedback(
                    reservation_id=reservation.id,
                    rating=feedback_rating,
                    review="Great stay",
                )
            )
            session.commit()

    monkeypatch.setenv("DATABASE_PATH", str(database_path))
    monkeypatch.setenv("HOTEL_TIMEZONE", "UTC")
    get_settings.cache_clear()
    at = AppTest.from_file(str(APP_PATH), default_timeout=10).run()
    at.radio[0].set_value("Manage reservation").run()
    at.text_input[0].set_value("012-345")
    at.button[0].click().run()
    assert not at.exception
    return at, engine


def test_customer_rates_completed_stay(tmp_path, monkeypatch):
    today = date.today()
    at, engine = setup_app(
        tmp_path, monkeypatch, today - timedelta(days=3), today - timedelta(days=1)
    )
    assert "Cancel reservation" not in [button.label for button in at.button]
    assert len(at.text_area) == 1

    at.button[1].click().run()
    assert any("choose a rating" in item.value for item in at.error)
    with Session(engine) as session:
        assert session.exec(select(Feedback)).all() == []

    at.radio[1].set_value(5)
    at.text_area[0].set_value("Mimi loved it.")
    at.button[1].click().run()
    assert not at.exception
    assert any("Thank you" in item.value for item in at.success)
    assert any("5/5" in item.value for item in at.markdown)
    assert len(at.text_area) == 0
    with Session(engine) as session:
        stored = session.exec(select(Feedback)).one()
    assert (stored.rating, stored.review) == (5, "Mimi loved it.")


def test_reviewed_stay_shows_feedback_without_form(tmp_path, monkeypatch):
    today = date.today()
    at, _ = setup_app(
        tmp_path, monkeypatch, today - timedelta(days=3), today, feedback_rating=4
    )
    assert any("Thank you" in item.value for item in at.success)
    assert any("4/5" in item.value for item in at.markdown)
    assert len(at.text_area) == 0


def test_future_stay_has_no_feedback_form(tmp_path, monkeypatch):
    today = date.today()
    at, _ = setup_app(
        tmp_path, monkeypatch, today + timedelta(days=5), today + timedelta(days=7)
    )
    assert any("Feedback opens" in item.value for item in at.info)
    assert len(at.text_area) == 0
    assert "Cancel reservation" in [button.label for button in at.button]
