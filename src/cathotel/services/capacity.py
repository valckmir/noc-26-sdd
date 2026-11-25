import csv
from datetime import date
from typing import TextIO

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
        date_text = row["date"].strip()
        try:
            capacity_date = date.fromisoformat(date_text)
            if capacity_date.isoformat() != date_text:
                raise ValueError("date is not in canonical ISO format")
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
        active_reservations = session.exec(
            select(Reservation).where(
                Reservation.status == ReservationStatus.ACTIVE,
                Reservation.arrival_date <= max(dates),
                Reservation.departure_date > min(dates),
            )
        ).all()
        reservation_counts = {
            capacity_date: sum(
                reservation.arrival_date <= capacity_date < reservation.departure_date
                for reservation in active_reservations
            )
            for capacity_date in dates
        }

        for row in rows:
            reservation_count = reservation_counts.get(row.date, 0)
            if row.room_capacity < reservation_count:
                raise CapacityImportError(
                    f"date {row.date.isoformat()}: capacity {row.room_capacity} is "
                    f"below its {reservation_count} active reservations"
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
