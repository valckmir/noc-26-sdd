from datetime import UTC, date as Date, datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint
from sqlmodel import Field, SQLModel


class ReservationStatus(StrEnum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class CapacityDate(SQLModel, table=True):
    __tablename__ = "capacity_date"
    __table_args__ = (CheckConstraint("room_capacity >= 0"),)

    date: Date = Field(primary_key=True)
    room_capacity: int


class Reservation(SQLModel, table=True):
    __tablename__ = "reservation"
    __table_args__ = (
        CheckConstraint("length(code) = 6 AND code NOT GLOB '*[^0-9]*'"),
        CheckConstraint("departure_date > arrival_date"),
    )

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True, min_length=6, max_length=6)
    arrival_date: Date
    departure_date: Date
    cat_name: str = Field(min_length=1)
    breed: str = Field(min_length=1)
    is_social: bool
    daily_walks_required: bool
    wellness_bath: bool = False
    wellness_massage: bool = False
    wellness_claw_trimming: bool = False
    premium_cat_food: bool = False
    status: ReservationStatus = ReservationStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def display_code(self) -> str:
        return f"{self.code[:3]}-{self.code[3:]}"


REVIEW_MAX_LENGTH = 500


class Feedback(SQLModel, table=True):
    __tablename__ = "feedback"
    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5"),
        CheckConstraint(f"review IS NULL OR length(review) <= {REVIEW_MAX_LENGTH}"),
    )

    id: int | None = Field(default=None, primary_key=True)
    reservation_id: int = Field(foreign_key="reservation.id", unique=True)
    rating: int = Field(ge=1, le=5)
    review: str | None = Field(default=None, max_length=REVIEW_MAX_LENGTH)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
