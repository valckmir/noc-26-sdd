# Quickstart: Cat Room Booking

## Prerequisites

- Python 3.13 and uv installed.
- The project dependencies installed from `pyproject.toml` with `uv sync`.
- A `.env` file or environment variables defining `HOTEL_TIMEZONE` (an IANA
  timezone such as `Europe/Prague`) and the SQLite database location.

## Run the customer application

```sh
uv run streamlit run src/cathotel/web.py
```

Expected result: the customer booking interface opens; past dates cannot be
selected, and staff capacity-upload controls are absent.

## Import capacity as staff

Create a UTF-8 CSV using the header and date format in
[staff-cli.md](contracts/staff-cli.md), then run:

```sh
uv run cathotel capacity import ./capacity.csv
```

Expected result: valid dates are imported atomically; malformed data or a
capacity reduction below active bookings returns an error without partial
updates.

## Validate customer journeys

```sh
uv run pytest
```

Acceptance coverage should demonstrate:

1. An available stay can be confirmed with cat details and optional services;
   the interface shows a unique `NNN-NNN` code.
2. Unavailable or incomplete booking attempts do not create reservations, and
   concurrent bookings do not exceed capacity.
3. The code retrieves the correct reservation and cancellation releases capacity
   only through the end of the local cutoff date.
4. Past stay dates are rejected by both the UI and service validation.
5. CSV import updates listed dates atomically and rejects invalid or conflicting
   files without partial application.

See [data-model.md](data-model.md) for domain invariants and the contracts in
[contracts/](contracts/) for user-facing and CLI behavior.
