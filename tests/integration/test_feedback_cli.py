from datetime import UTC, date, datetime

from sqlmodel import Session
from typer.testing import CliRunner

from cathotel import cli
from cathotel.config import Settings
from cathotel.database import create_database_engine, create_db_and_tables
from cathotel.models import Feedback, Reservation

runner = CliRunner()


def use_database(tmp_path, monkeypatch):
    database_path = tmp_path / "staff.sqlite"
    monkeypatch.setattr(
        cli,
        "get_settings",
        lambda: Settings(database_path=database_path, hotel_timezone="UTC"),
    )
    engine = create_database_engine(database_path)
    create_db_and_tables(engine)
    return engine


def test_feedback_list_shows_entries_newest_first_and_average(tmp_path, monkeypatch):
    engine = use_database(tmp_path, monkeypatch)
    with Session(engine) as session:
        for code, rating, review, day in (
            ("111111", 5, "Lovely staff.", 1),
            ("222222", 4, None, 2),
        ):
            reservation = Reservation(
                code=code,
                arrival_date=date(2030, 3, 1),
                departure_date=date(2030, 3, 3),
                cat_name="Mimi",
                breed="Tabby",
                is_social=True,
                daily_walks_required=False,
            )
            session.add(reservation)
            session.commit()
            session.add(
                Feedback(
                    reservation_id=reservation.id,
                    rating=rating,
                    review=review,
                    created_at=datetime(2030, 3, 3 + day, tzinfo=UTC),
                )
            )
            session.commit()

    result = runner.invoke(cli.app, ["feedback", "list"])

    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert lines[0] == "2030-03-05  222-222  stay 2030-03-01 to 2030-03-03  rating 4/5"
    assert lines[1] == "2030-03-04  111-111  stay 2030-03-01 to 2030-03-03  rating 5/5"
    assert lines[2] == "  Lovely staff."
    assert lines[3] == "2 feedback entries, average rating 4.5/5"


def test_feedback_list_without_feedback(tmp_path, monkeypatch):
    use_database(tmp_path, monkeypatch)
    result = runner.invoke(cli.app, ["feedback", "list"])
    assert result.exit_code == 0
    assert result.output.strip() == "No feedback yet."
