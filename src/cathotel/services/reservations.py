import secrets
from datetime import date, timedelta
from typing import Callable

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from cathotel.models import CapacityDate, Reservation, ReservationStatus
from cathotel.services.dates import facility_today


class ReservationError(ValueError):
    pass


def _occupied_nights(arrival_date: date, departure_date: date):
    night = arrival_date
    while night < departure_date:
        yield night
        night += timedelta(days=1)


def _available_for_night(session: Session, night: date) -> bool:
    capacity = session.get(CapacityDate, night)
    if capacity is None:
        return False
    reservations = session.exec(
        select(func.count(Reservation.id)).where(
            Reservation.status == ReservationStatus.ACTIVE,
            Reservation.arrival_date <= night,
            Reservation.departure_date > night,
        )
    ).one()
    return reservations < capacity.room_capacity


def check_availability(
    session: Session, arrival_date: date, departure_date: date
) -> bool:
    if departure_date <= arrival_date:
        return False
    return all(
        _available_for_night(session, night)
        for night in _occupied_nights(arrival_date, departure_date)
    )


def _random_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def create_reservation(
    session: Session,
    *,
    arrival_date: date,
    departure_date: date,
    cat_name: str,
    breed: str,
    is_social: bool,
    daily_walks_required: bool,
    hotel_timezone: str,
    today: date | None = None,
    code_factory: Callable[[], str] | None = None,
    wellness_bath: bool = False,
    wellness_massage: bool = False,
    wellness_claw_trimming: bool = False,
    premium_cat_food: bool = False,
) -> Reservation:
    current_date = today or facility_today(hotel_timezone)
    if arrival_date < current_date:
        raise ReservationError("arrival date cannot be in the past")
    if departure_date <= arrival_date:
        raise ReservationError("departure date must be after arrival date")

    clean_name = cat_name.strip()
    clean_breed = breed.strip()
    if not clean_name:
        raise ReservationError("cat name is required")
    if not clean_breed:
        raise ReservationError("breed is required")

    try:
        session.connection().exec_driver_sql("BEGIN IMMEDIATE")
        if not check_availability(session, arrival_date, departure_date):
            raise ReservationError("no room is available for every night in this stay")

        make_code = code_factory or _random_code
        reservation = None
        for _ in range(100):
            code = make_code()
            if len(code) != 6 or not code.isdigit():
                raise ReservationError("reservation code generator must return six digits")
            if session.exec(
                select(Reservation.id).where(Reservation.code == code)
            ).first() is not None:
                continue
            reservation = Reservation(
                code=code,
                arrival_date=arrival_date,
                departure_date=departure_date,
                cat_name=clean_name,
                breed=clean_breed,
                is_social=is_social,
                daily_walks_required=daily_walks_required,
                wellness_bath=wellness_bath,
                wellness_massage=wellness_massage,
                wellness_claw_trimming=wellness_claw_trimming,
                premium_cat_food=premium_cat_food,
            )
            session.add(reservation)
            try:
                session.flush()
                break
            except IntegrityError:
                session.rollback()
                session.connection().exec_driver_sql("BEGIN IMMEDIATE")
                reservation = None
        if reservation is None:
            raise ReservationError("could not allocate a unique reservation code")
        session.commit()
        session.refresh(reservation)
        session.expunge(reservation)
        return reservation
    except Exception:
        session.rollback()
        raise


def get_reservation(session: Session, code: str) -> Reservation | None:
    normalized = code.strip().replace("-", "")
    if len(normalized) != 6 or not normalized.isdigit():
        return None
    return session.exec(
        select(Reservation).where(Reservation.code == normalized)
    ).first()


def cancel_reservation(
    session: Session,
    code: str,
    *,
    hotel_timezone: str,
    today: date | None = None,
) -> Reservation:
    normalized = code.strip().replace("-", "")
    try:
        session.connection().exec_driver_sql("BEGIN IMMEDIATE")
        reservation = get_reservation(session, normalized)
        if reservation is None:
            raise ReservationError("reservation code was not found")
        if reservation.status == ReservationStatus.CANCELLED:
            session.commit()
            session.refresh(reservation)
            session.expunge(reservation)
            return reservation

        current_date = today or facility_today(hotel_timezone)
        cancellation_deadline = reservation.arrival_date - timedelta(days=2)
        if current_date > cancellation_deadline:
            raise ReservationError("cancellation deadline has passed")

        reservation.status = ReservationStatus.CANCELLED
        session.add(reservation)
        session.commit()
        session.refresh(reservation)
        session.expunge(reservation)
        return reservation
    except Exception:
        session.rollback()
        raise
