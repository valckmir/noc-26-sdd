from datetime import date

import pytest
from sqlmodel import Session, select

from cathotel.database import create_database_engine, create_db_and_tables
from cathotel.services import feedback as feedback_service
from cathotel.models import Feedback, Reservation, ReservationStatus
from cathotel.services.feedback import (
    FeedbackError,
    average_rating,
    can_leave_feedback,
    list_feedback,
    submit_feedback,
)

ARRIVAL = date(2030, 3, 10)
DEPARTURE = date(2030, 3, 12)


@pytest.fixture
def session(tmp_path):
    engine = create_database_engine(tmp_path / "feedback.sqlite")
    create_db_and_tables(engine)
    with Session(engine) as db_session:
        yield db_session


def add_reservation(session, code="012345", status=ReservationStatus.ACTIVE):
    reservation = Reservation(
        code=code,
        arrival_date=ARRIVAL,
        departure_date=DEPARTURE,
        cat_name="Mimi",
        breed="Tabby",
        is_social=True,
        daily_walks_required=False,
        status=status,
    )
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation


def submit(session, code="012-345", rating=5, review=None, today=DEPARTURE):
    return submit_feedback(
        session, code, rating, review, hotel_timezone="UTC", today=today
    )


def test_eligibility_starts_on_departure_day_for_active_reservations(session):
    reservation = add_reservation(session)
    assert not can_leave_feedback(reservation, date(2030, 3, 11))
    assert can_leave_feedback(reservation, DEPARTURE)
    assert can_leave_feedback(reservation, date(2031, 1, 1))
    cancelled = add_reservation(session, code="111111", status=ReservationStatus.CANCELLED)
    assert not can_leave_feedback(cancelled, date(2031, 1, 1))


def test_submit_stores_rating_and_trimmed_review(session):
    reservation = add_reservation(session)
    feedback = submit(session, rating=4, review="  Lovely staff.  ")
    assert feedback.reservation_id == reservation.id
    assert feedback.rating == 4
    assert feedback.review == "Lovely staff."


def test_whitespace_review_is_stored_as_none(session):
    add_reservation(session)
    assert submit(session, review="   ").review is None


@pytest.mark.parametrize("rating", [None, 0, 6, True, 3.5])
def test_invalid_or_missing_rating_is_rejected(session, rating):
    add_reservation(session)
    with pytest.raises(FeedbackError, match="rating|Rating"):
        submit(session, rating=rating)
    assert session.exec(select(Feedback)).all() == []


def test_review_longer_than_limit_is_rejected(session):
    add_reservation(session)
    with pytest.raises(FeedbackError, match="500"):
        submit(session, review="x" * 501)
    assert submit(session, review="x" * 500).review == "x" * 500


def test_ineligible_reservations_are_refused(session):
    add_reservation(session)
    with pytest.raises(FeedbackError, match="departure date"):
        submit(session, today=date(2030, 3, 11))
    add_reservation(session, code="222222", status=ReservationStatus.CANCELLED)
    with pytest.raises(FeedbackError, match="cancelled"):
        submit(session, code="222-222")
    with pytest.raises(FeedbackError, match="could not be used"):
        submit(session, code="999-999")
    assert session.exec(select(Feedback)).all() == []


def test_only_one_feedback_per_reservation(session):
    add_reservation(session)
    submit(session, rating=5)
    with pytest.raises(FeedbackError, match="already submitted"):
        submit(session, rating=1)
    assert [item.rating for item in session.exec(select(Feedback)).all()] == [5]


def test_database_rejects_duplicate_feedback_from_concurrent_submissions(
    session, monkeypatch
):
    reservation = add_reservation(session)
    session.add(Feedback(reservation_id=reservation.id, rating=3))
    session.commit()
    monkeypatch.setattr(feedback_service, "get_feedback", lambda *_: None)
    with pytest.raises(FeedbackError, match="already submitted"):
        submit(session)


def test_list_is_newest_first_with_average(session):
    add_reservation(session, code="111111")
    add_reservation(session, code="222222")
    submit(session, code="111-111", rating=5)
    submit(session, code="222-222", rating=2)
    entries = list_feedback(session)
    assert [entry.reservation.code for entry in entries] == ["222222", "111111"]
    assert average_rating(entries) == 3.5
    assert average_rating([]) is None
