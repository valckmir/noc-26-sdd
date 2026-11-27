from dataclasses import dataclass
from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from cathotel.models import REVIEW_MAX_LENGTH, Feedback, Reservation, ReservationStatus
from cathotel.services.dates import facility_today
from cathotel.services.reservations import get_reservation


class FeedbackError(ValueError):
    pass


@dataclass(frozen=True)
class FeedbackEntry:
    feedback: Feedback
    reservation: Reservation


def can_leave_feedback(reservation: Reservation, today: date) -> bool:
    return (
        reservation.status == ReservationStatus.ACTIVE
        and reservation.departure_date <= today
    )


def get_feedback(session: Session, reservation: Reservation) -> Feedback | None:
    return session.exec(
        select(Feedback).where(Feedback.reservation_id == reservation.id)
    ).first()


def submit_feedback(
    session: Session,
    code: str,
    rating: int | None,
    review: str | None = None,
    *,
    hotel_timezone: str,
    today: date | None = None,
) -> Feedback:
    if rating is None:
        raise FeedbackError("Please choose a rating from 1 to 5.")
    if isinstance(rating, bool) or not isinstance(rating, int) or not 1 <= rating <= 5:
        raise FeedbackError("Rating must be a whole number from 1 to 5.")
    clean_review = (review or "").strip() or None
    if clean_review is not None and len(clean_review) > REVIEW_MAX_LENGTH:
        raise FeedbackError(f"Review must be at most {REVIEW_MAX_LENGTH} characters.")

    reservation = get_reservation(session, code)
    if reservation is None:
        raise FeedbackError("Reservation code could not be used.")
    current_date = today or facility_today(hotel_timezone)
    if reservation.status != ReservationStatus.ACTIVE:
        raise FeedbackError("Feedback cannot be left for a cancelled reservation.")
    if not can_leave_feedback(reservation, current_date):
        raise FeedbackError("Feedback opens on your departure date.")
    if get_feedback(session, reservation) is not None:
        raise FeedbackError("Feedback was already submitted for this reservation.")

    feedback = Feedback(
        reservation_id=reservation.id,
        rating=rating,
        review=clean_review,
    )
    session.add(feedback)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise FeedbackError(
            "Feedback was already submitted for this reservation."
        ) from error
    session.refresh(feedback)
    return feedback


def list_feedback(session: Session) -> list[FeedbackEntry]:
    rows = session.exec(
        select(Feedback, Reservation)
        .join(Reservation, Feedback.reservation_id == Reservation.id)
        .order_by(Feedback.created_at.desc(), Feedback.id.desc())
    ).all()
    return [FeedbackEntry(feedback=feedback, reservation=reservation) for feedback, reservation in rows]


def average_rating(entries: list[FeedbackEntry]) -> float | None:
    if not entries:
        return None
    return sum(entry.feedback.rating for entry in entries) / len(entries)
