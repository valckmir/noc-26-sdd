# Data Model: Customer Stay Feedback

## Feedback (new)

One customer assessment of one completed stay.

| Field | Type | Rules |
|---|---|---|
| id | integer | Internal generated identity |
| reservation_id | integer | Required; foreign key to `reservation.id`; UNIQUE (one feedback per reservation) |
| rating | integer | Required; whole number 1–5 (CHECK constraint) |
| review | string or null | Optional; trimmed; null when empty; at most 500 characters |
| created_at | datetime | Required; submission instant (UTC) |

## Reservation (existing, unchanged columns)

Feedback eligibility is derived, not stored:

- `status == active` and
- `departure_date <= facility_today(HOTEL_TIMEZONE)`

## Invariants

- A reservation has zero or one feedback; feedback is never updated or deleted by customers.
- Feedback exists only for reservations that were eligible at submission time.
- Average rating = mean of all `Feedback.rating`, shown to one decimal place; undefined (not shown) when there is no feedback.
