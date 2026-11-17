from datetime import date

import pytest
from sqlmodel import Session, select

from cathotel.database import create_database_engine, create_db_and_tables
from cathotel.models import CapacityDate, Reservation
from cathotel.services.reservations import (
    ReservationError,
    check_availability,
    create_reservation,
)


@pytest.fixture

def session(tmp_path):
    engine = create_database_engine(tmp_path / "booking.sqlite")
    create_db_and_tables(engine)
    with Session(engine) as db_session:
        yield db_session


def add_capacity(session, start=date(2030, 1, 1), days=5, rooms=2):
    from datetime import timedelta

    for offset in range(days):
        session.add(CapacityDate(date=start + timedelta(days=offset), room_capacity=rooms))
    session.commit()


def details(**overrides):
    values = {
        "arrival_date": date(2030, 1, 1),
        "departure_date": date(2030, 1, 3),
        "cat_name": "Mimi",
        "breed": "Tabby",
        "is_social": True,
        "daily_walks_required": False,
        "hotel_timezone": "UTC",
        "today": date(2029, 12, 1),
    }
    values.update(overrides)
    return values


def test_availability_requires_capacity_for_every_occupied_night(session):
    session.add(CapacityDate(date=date(2030, 1, 1), room_capacity=1))
    session.commit()

    assert not check_availability(session, date(2030, 1, 1), date(2030, 1, 3))


def test_past_or_invalid_date_ranges_are_rejected(session):
    add_capacity(session)
    with pytest.raises(ReservationError):
        create_reservation(session, **details(arrival_date=date(2029, 12, 31)))
    with pytest.raises(ReservationError):
        create_reservation(session, **details(departure_date=date(2030, 1, 1)))


def test_required_cat_details_are_trimmed_and_validated(session):
    add_capacity(session)
    with pytest.raises(ReservationError, match="cat name"):
        create_reservation(session, **details(cat_name="  "))
    with pytest.raises(ReservationError, match="breed"):
        create_reservation(session, **details(breed=" \t"))


def test_booking_persists_code_and_all_optional_services(session):
    add_capacity(session)
    reservation = create_reservation(
        session,
        **details(
            code_factory=lambda: "000123",
            wellness_bath=True,
            wellness_massage=True,
            wellness_claw_trimming=True,
            premium_cat_food=True,
        ),
    )

    assert reservation.display_code == "000-123"
    assert reservation.cat_name == "Mimi"
    assert reservation.wellness_bath
    assert reservation.wellness_massage
    assert reservation.wellness_claw_trimming
    assert reservation.premium_cat_food
    assert session.get(Reservation, reservation.id).code == "000123"


def test_unavailable_or_missing_capacity_prevents_creation(session):
    add_capacity(session, rooms=0)
    with pytest.raises(ReservationError, match="available"):
        create_reservation(session, **details())
    assert session.exec(select(Reservation)).all() == []


def test_booking_counts_overlapping_reservations_and_rejects_full_night(session):
    add_capacity(session, rooms=1)
    create_reservation(session, **details(departure_date=date(2030, 1, 2)))

    with pytest.raises(ReservationError, match="available"):
        create_reservation(session, **details(arrival_date=date(2030, 1, 1)))
