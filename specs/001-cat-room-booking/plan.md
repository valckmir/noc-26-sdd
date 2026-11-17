# Implementation Plan: Cat Room Booking

**Branch**: `001-cat-room-booking` | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-cat-room-booking/spec.md`

## Summary

Build a customer-only cat-room booking application with Streamlit. Staff capacity
management is a separate Typer CLI command that imports CSV capacity data.
SQLModel models and services use SQLite for capacity and reservation data;
Pydantic Settings loads configuration from environment variables and `.env`.
The booking flow checks every night in a requested stay and atomically records a
reservation with a unique `NNN-NNN` code. Customers use that code to view or
cancel within the defined cutoff. Dependencies are managed with uv.

## Technical Context

**Language/Version**: Python 3.13 (from `pyproject.toml`)

**Primary Dependencies**: Streamlit, Typer, SQLModel, Pydantic Settings

**Storage**: SQLite

**Testing**: pytest; unit tests for services and validation, CLI tests for CSV
imports, and Streamlit-facing integration tests for customer journeys

**Target Platform**: Python 3.13 environment; local/single-facility deployment

**Project Type**: Single Python web application with a staff CLI

**Performance Goals**: For the initial single-facility scope, customer actions
and CSV imports of up to 10,000 rows complete within 2 seconds at p95, excluding
initial application startup. This is a planning target, not a scale guarantee.

**Constraints**: All reservation and capacity business rules MUST live in
services, not Streamlit views or Typer command handlers. SQLite transactions
MUST prevent overbooking. Capacity CSV import is all-or-nothing. Staff uses the
CLI rather than customer web pages. `HOTEL_TIMEZONE` MUST be configured to the
facility's local IANA time zone so cancellation deadlines use local calendar
dates. Reservation codes are randomly generated six-digit numbers displayed as
`NNN-NNN`; uniqueness MUST be enforced despite the finite code space, retrying
on collision. Configuration MUST be loaded
through Pydantic Settings, with `.env` supported. Dependencies MUST be managed
with uv.

**Scale/Scope**: One facility, one room category, one cat per reservation, and
initial CSV imports up to 10,000 capacity rows. No customer accounts, payments,
notifications, reservation edits, or staff web interface.

## Constitution Check

- **Customer-centered simplicity**: Pass. The customer journey contains one room
  option and only requested stay, cat, and optional service choices.
- **Layered business logic**: Pass. Availability, validation, booking,
  cancellation, and capacity-import rules are assigned to services. Streamlit
  views and Typer commands are input/output adapters.
- **Simplicity over complexity**: Pass. One Python project, SQLite, and direct
  SQLModel use avoid unnecessary infrastructure and abstraction layers.
- **Role-aware experiences**: Pass. Customer web UI and staff CLI are distinct
  access surfaces; the customer interface will not expose capacity management.
- **Intentional code comments**: Pass. Comments are reserved for explaining
  non-obvious decisions, not restating implementation.

No constitution violations identified. The distinct customer UI and staff CLI
are explicitly required access surfaces, not additional product roles or
unnecessary layers.

## Project Structure

### Documentation (this feature)

```text
specs/001-cat-room-booking/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    ├── customer-ui.md
    └── staff-cli.md
```

### Source Code (repository root)

```text
src/cathotel/
├── __init__.py
├── config.py          # Pydantic Settings and .env configuration
├── database.py        # SQLite engine/session setup
├── models.py          # SQLModel business and persistence models
├── services/
│   ├── capacity.py    # Capacity CSV validation and import rules
│   └── reservations.py# Availability, reservation, code, and cancellation rules
├── web.py             # Streamlit customer interface
└── cli.py             # Typer staff capacity commands

tests/
├── unit/
├── integration/
└── acceptance/
```

**Structure Decision**: Keep a single Python package under the existing
`src/cathotel` layout. Put all business rules in focused service modules;
Streamlit and Typer only collect input, call services, and display results.
Avoid repository abstractions unless direct SQLModel service use proves
insufficient.

## Complexity Tracking

No constitution violations or unjustified architectural complexity.
