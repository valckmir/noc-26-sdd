# Data Model: Cat Room Booking

## CapacityDate

One record per calendar night with capacity supplied by staff.

| Field | Type | Rules |
|---|---|---|
| date | date | Required; unique primary/business key |
| room_capacity | integer | Required; non-negative whole number |

Availability is `room_capacity` minus active reservations whose occupied-night
range contains this date. A date without a capacity record is unavailable.

## Reservation

One cat's room stay, created as active immediately upon successful confirmation.

| Field | Type | Rules |
|---|---|---|
| id | integer | Internal generated identity |
| code | string | Required; randomly generated; unique; six digits displayed as `NNN-NNN` |
| arrival_date | date | Required; current or future date in facility timezone |
| departure_date | date | Required; strictly after arrival date |
| cat_name | string | Required; non-empty after trimming whitespace |
| breed | string | Required; non-empty after trimming whitespace |
| is_social | boolean | Required |
| daily_walks_required | boolean | Required |
| wellness_bath | boolean | Optional service selection; defaults false |
| wellness_massage | boolean | Optional service selection; defaults false |
| wellness_claw_trimming | boolean | Optional service selection; defaults false |
| premium_cat_food | boolean | Optional service selection; defaults false |
| status | enum/string | Required; `active` or `cancelled`; defaults `active` |
| created_at | datetime | Required; creation instant |

Arrival is included and departure is excluded from occupied nights. One active
reservation consumes one room for each occupied night. Cancelled reservations
do not consume capacity and remain available for lookup by code.

## Relationships and invariants

- `CapacityDate.date` is unique; CSV imports update dates present in the file and
  leave omitted dates unchanged.
- A reservation spans every date in `[arrival_date, departure_date)` and can be
  confirmed only if capacity is available on every date.
- The booking transaction rechecks capacity and creates the reservation
  atomically; active reservations never exceed a date's capacity.
- A capacity import is atomic and cannot reduce any affected date below its
  active reservation count.
- `Reservation.code` is a randomly generated, unique six-digit number rendered
  as three digits, hyphen, three digits (`NNN-NNN`). Retain leading zeros when
  storing and displaying the code; retry generation if a code collision occurs.
- Cancellation changes `active` to `cancelled` only when the facility-local date
  is no later than two calendar days before arrival. Repeated cancellation does
  not release capacity twice.
