# Research: Customer Stay Feedback

## R1. Where customers give feedback

- **Decision**: Add a feedback section to the existing "Manage reservation" page, shown after a successful code lookup.
- **Rationale**: The app is accountless; the reservation code is the only proof of a stay. Reusing the lookup avoids a new page and a second code entry.
- **Alternatives considered**: Separate "Leave feedback" page (duplicates the lookup); emailed link (no notifications exist).

## R2. When feedback is allowed

- **Decision**: Active reservation and `facility_today(HOTEL_TIMEZONE) >= departure_date`.
- **Rationale**: Feedback is about services received; the cat has left on the departure day. Cancelled stays received no services.
- **Alternatives considered**: From arrival day (feedback before services are complete).

## R3. One feedback per reservation

- **Decision**: `feedback.reservation_id` has a UNIQUE constraint. The service checks first for a friendly message, and maps an `IntegrityError` from a concurrent insert to the same "already submitted" error.
- **Rationale**: The database guarantees SC-004 even with two browser tabs; no locking code needed.

## R4. Rating input in Streamlit

- **Decision**: `st.radio` with options 1–5, `index=None`, horizontal, inside an `st.form`; review via `st.text_area(max_chars=500)`.
- **Rationale**: Works with `AppTest`; `index=None` forces an explicit choice so a missing rating can be reported. `st.feedback("stars")` was considered but is less predictable in `AppTest`.

## R5. Staff access to feedback

- **Decision**: `cathotel feedback list` Typer command printing entries newest first and a summary line.
- **Rationale**: Staff already use the CLI (feature 001); keeps all staff actions out of the customer web app (Principle IV).
- **Alternatives considered**: CSV export (not requested); staff web page (needs staff auth, which does not exist).

## R6. Schema creation

- **Decision**: `SQLModel.metadata.create_all()` (already called by web and CLI) creates the new table in existing databases.
- **Rationale**: Adding a table needs no migration; existing tables are untouched.
