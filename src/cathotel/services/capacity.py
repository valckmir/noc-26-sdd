import csv
from datetime import date
from typing import TextIO

from sqlalchemy import func
from sqlmodel import Session, select

from cathotel.models import CapacityDate, Reservation, ReservationStatus


class CapacityImportError(ValueError):
    pass


def _parse_capacity_csv(file: TextIO) -> list[CapacityDate]:
    reader = csv.DictReader(file)
    if reader.fieldnames != ["date", "room_capacity"]:
        raise CapacityImportError(
            "CSV header must contain exactly: date,room_capacity"
        )

    rows: list[CapacityDate] = []
    seen_dates: set[date] = set()
    for line_number, row in enumerate(reader, start=2):
        if None in row or row.get("date") is None or row.get("room_capacity") is None:
            raise CapacityImportError(f"row {line_number}: expected exactly two columns")
        try:
            capacity_date = date.fromisoformat(row["date"].strip())
        except ValueError as error:
            raise CapacityImportError(
                f"row {line_number}: date must use ISO YYYY-MM-DD format"
            ) from error
        try:
            capacity = int(row["room_capacity"].strip())
        except ValueError as error:
            raise CapacityImportError(
                f"row {line_number}: room_capacity must be a non-negative whole number"
            ) from error
        if capacity < 0:
            raise CapacityImportError(
                f"row {line_number}: room_capacity must be a non-negative whole number"
            )
        if capacity_date in seen_dates:
            raise CapacityImportError(
                f"row {line_number}: duplicate date {capacity_date.isoformat()}"
            )
        seen_dates.add(capacity_date)
        rows.append(CapacityDate(date=capacity_date, room_capacity=capacity))

    if not rows:
        raise CapacityImportError("CSV must contain at least one capacity row")
    return rows


def import_capacity_csv(session: Session, file: TextIO) -> int:
    rows = _parse_capacity_csv(file)
    dates = [row.date for row in rows]
    try:
        existing_capacity = {
            item.date: item
            for item in session.exec(
                select(CapacityDate).where(CapacityDate.date.in_(dates))
            ).all()
        }
        reservation_counts = dict(
            session.exec(
                select(Reservation.arrival_date, func.count(Reservation.id))
                .where(
                    Reservation.status == ReservationStatus.ACTIVE,
                    Reservation.arrival_date.in_(dates),
                )
                .group_by(Reservation.arrival_date)
            ).all()
        )

        for row in rows:
            active_reservations = reservation_counts.get(row.date, 0)
            if row.room_capacity < active_reservations:
                raise CapacityImportError(
                    f"date {row.date.isoformat()}: capacity {row.room_capacity} is "
                    f"below its {active_reservations} active reservations"
                )

        for row in rows:
            stored = existing_capacity.get(row.date)
            if stored is None:
                session.add(row)
            else:
                stored.room_capacity = row.room_capacity
        session.commit()
    except Exception:
        session.rollback()
        raise
    return len(rows)
