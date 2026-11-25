# CatHotel

CatHotel is a simple booking application for cat stays. Customers use the
Streamlit web interface to check room availability, book a stay, and manage a
reservation using its code. Staff load daily room capacity through the Typer
command-line interface.

## Requirements

- Python 3.13
- [uv](https://docs.astral.sh/uv/)

## Setup

Install the project and development dependencies:

```sh
uv sync
```

Copy `.env.example` to `.env` and set `HOTEL_TIMEZONE` to the facility's IANA
timezone. `DATABASE_PATH` defaults to `cathotel.db` in the project directory.
The same settings and SQLite database must be used by both the web application
and the staff CLI.

```sh
cp .env.example .env
```

## Run the customer application

```sh
uv run streamlit run src/cathotel/web.py
```

The customer UI supports date-based availability checks, immediate bookings,
and reservation-code lookup/cancellation. It does not expose staff capacity
management or require customer accounts.

## Import capacity as staff

Prepare a UTF-8 CSV with exactly `date,room_capacity` columns, ISO `YYYY-MM-DD`
dates, and non-negative whole-number capacities. See
[`examples/capacity.csv`](examples/capacity.csv).

```sh
uv run cathotel capacity import examples/capacity.csv
```

The import is all-or-nothing: invalid rows and capacity reductions below active
reservations are rejected without applying partial changes. Run the CLI only
from the staff environment with access to the application database.

## Run validation

```sh
uv run pytest
```
