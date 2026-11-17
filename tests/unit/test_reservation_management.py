from datetime import date

import pytest
from sqlmodel import Session

from cathotel.database import create_database_engine, create_db_and_tables
from cathotel.models import CapacityDate, Reservation, ReservationStatus
from cathotel.services.reservations import (
    ReservationError,
    cancel_reservation,
    get_reservation,
)
from cathotel.services.reservations import create_reservation


@pytest.fixture

def session(tmp_path):
    engine = create_database_engine(tmp_path / "management.sqlite")
    create_db_and_tables(engine)
    with Session(engine) as db_session:
        yield db_session


def booking(session):
    session.add_all(
        [
            CapacityDate(date=date(2030, 3, 10), room_capacity=2),
            CapacityDate(date=date(2030, 3, 11), room_capacity=2),
            CapacityDate(date=date(2030, 3, 12), room_capacity=2),
            CapacityDate(date=date(2030, 3, 13), room_capacity=2),
        ]
    )
    session.commit()
    return create_reservation(
        session,
        arrival_date=date(2030, 3, 12),
        departure_date=date(2030, 3, 14),
        cat_name="Mimi",
        breed="Tabby",
        is_social=True,
        daily_walks_required=False,
        hotel_timezone="UTC",
        today=date(2030, 3, 1),
        code_factory=lambda: "012345",
    )


def test_lookup_returns_reservation_for_formatted_or_unformatted_code(session):
    reservation = booking(session)

    assert get_reservation(session, "012345").id == reservation.id
    assert get_reservation(session, "012-345").id == reservation.id
    assert get_reservation(session, "999-999") is None


def test_cancellation_allowed_on_cutoff_date_and_releases_capacity_once(session):
    reservation = booking(session)

    cancelled = cancel_reservation(
        session,
        reservation.display_code,
        hotel_timezone="UTC",
        today=date(2030, 3, 10),
    )
    assert cancelled.status == ReservationStatus.CANCELLED
    assert cancel_reservation(
        session,
        reservation.display_code,
        hotel_timezone="UTC",
        today=date(2030, 3, 10),
    ).status == ReservationStatus.CANCELLED


def test_cancellation_refused_after_cutoff_and_unknown_code_is_not_found(session):
    reservation = booking(session)
    with pytest.raises(ReservationError, match="deadline"):
        cancel_reservation(
            session,
            reservation.display_code,
            hotel_timezone="UTC",
            today=date(2030, 3, 11),
        )
    assert get_reservation(session, reservation.code).status == ReservationStatus.ACTIVE
    with pytest.raises(ReservationError, match="not found"):
        cancel_reservation(
            session,
            "999-999",
            hotel_timezone="UTC",
            today=date(2030, 3, 1),
        )
