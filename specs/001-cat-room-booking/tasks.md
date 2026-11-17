# Tasks: Cat Room Booking

**Input**: Design documents from `/specs/001-cat-room-booking/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, and `contracts/`

**Organization**: Tasks are grouped by the prioritized user stories: staff capacity definition (P1), customer booking (P2), then reservation lookup/cancellation (P3). Each story includes focused automated tests before its implementation.

## Phase 1: Setup

**Purpose**: Establish Python dependencies and runnable entry points.

- [X] T001 Add Streamlit, Typer, SQLModel, and Pydantic Settings dependencies in `pyproject.toml`, preserving the existing Python 3.13 and uv configuration.
- [X] T002 Add pytest as a uv development dependency in `pyproject.toml` under `[dependency-groups].dev`.
- [X] T003 [P] Create the services package initializer in `src/cathotel/services/__init__.py` and use `src/cathotel/cli.py` as the single Typer CLI module.
- [X] T004 Add or update the `cathotel` console entry point for the Typer CLI in `pyproject.toml`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Provide shared configuration, database initialization, and core domain models required by every story.

- [X] T005 Implement Pydantic Settings loading `.env`, SQLite database path, and required IANA `HOTEL_TIMEZONE` in `src/cathotel/config.py`.
- [X] T006 Implement SQLModel SQLite engine, session creation, and table initialization helpers in `src/cathotel/database.py`.
- [X] T007 Define the `CapacityDate` SQLModel in `src/cathotel/models.py` with `date` as the unique primary/business key and `room_capacity` as a required non-negative integer.
- [X] T008 Define the `Reservation` SQLModel in `src/cathotel/models.py` with a unique randomly generated six-digit code displayed as two three-digit groups, arrival/departure dates, non-empty trimmed cat name and breed, required social and daily-walk booleans, four optional service booleans defaulting false, active/cancelled status defaulting active, and creation timestamp.
- [X] T009 Implement shared facility-local date and cancellation-cutoff helpers in `src/cathotel/services/dates.py`, using the configured facility IANA timezone `HOTEL_TIMEZONE` for booking-date validation and a cutoff through the end of the local calendar date two calendar days before check-in.

**Checkpoint**: Shared settings, SQLite session, domain models, and date rules are available before story work.

---

## Phase 3: User Story 1 - Provide Room Capacity (Priority: P1) 🎯 MVP

**Goal**: Staff can import dated room capacities via the Typer CLI, with strict all-or-nothing validation and no customer-facing staff tools.

**Independent Test**: Invoke the CLI with a valid CSV and read back the `CapacityDate` rows from SQLite to verify each listed date and capacity; submit malformed, duplicate-date, or reservation-conflicting input and verify the command fails and the database remains unchanged.

### Tests for User Story 1

- [X] T010 [P] [US1] Add capacity-service tests for required CSV headers `date,room_capacity`, ISO `YYYY-MM-DD` dates, non-negative whole-number capacity, duplicate dates, omitted dates remaining unchanged, and all-or-nothing validation in `tests/unit/test_capacity_service.py`.
- [X] T011 [P] [US1] Add Typer CLI integration tests that verify successful imports by querying persisted `CapacityDate` rows in the test SQLite database, and verify actionable errors, non-zero failure exit status, and unchanged database contents after invalid imports in `tests/integration/test_capacity_cli.py`.

### Implementation for User Story 1

- [X] T012 [US1] Implement CSV parsing and validation in `src/cathotel/services/capacity.py`; require exactly `date,room_capacity`, ISO `YYYY-MM-DD`, non-negative whole-number capacities, and no duplicate date per file; reject the complete file if any row is invalid.
- [X] T013 [US1] Implement transactional capacity upsert in `src/cathotel/services/capacity.py`; update only dates present in the import, leave omitted dates unchanged, and reject the entire update if any new capacity is below its active reservation count.
- [X] T014 [US1] Implement the Typer `capacity import PATH` command in `src/cathotel/cli.py` using shared settings, SQLite sessions, and capacity service; report successful row count or actionable errors, return non-zero on failure, and keep staff upload controls out of `src/cathotel/web.py`.

**Checkpoint**: The staff CLI can define capacity and reject invalid updates atomically; customer UI remains separate.

---

## Phase 4: User Story 2 - Book a Cat's Stay (Priority: P2)

**Goal**: Customers select an allowed date range, see availability, enter required cat details and optional services, and immediately receive a reservation code when confirmed.

**Independent Test**: With capacity loaded, book an available stay and verify immediate confirmation with a unique `NNN-NNN` code; verify unavailable dates (including dates with no capacity record), invalid details, past dates, and competing last-room bookings cannot create an invalid or over-capacity reservation.

### Tests for User Story 2

- [X] T015 [P] [US2] Add reservation-service tests for past/invalid date ranges, every-night availability, dates without capacity being unavailable, required cat fields, optional service combinations, and capacity exhaustion in `tests/unit/test_reservation_booking.py`.
- [X] T016 [P] [US2] Add Streamlit AppTest coverage for past-date exclusion, unavailable range messaging, successful immediate confirmation, and random unique six-digit `NNN-NNN` code format in `tests/acceptance/test_customer_booking.py`.

### Implementation for User Story 2

- [X] T017 [US2] Implement reservation-code generation and uniqueness retry in `src/cathotel/services/reservations.py`; generate a random six-digit number, preserve leading zeros, display as `NNN-NNN`, and enforce uniqueness in SQLite by retrying collisions.
- [X] T018 [US2] Implement service-level date/detail validation and availability checks in `src/cathotel/services/reservations.py`; reject past arrival dates, require departure after arrival, count occupied nights as arrival-inclusive/departure-exclusive, require capacity on every occupied night, and treat dates without capacity as unavailable.
- [X] T019 [US2] Implement transactional reservation confirmation in `src/cathotel/services/reservations.py`; recheck every occupied night's capacity and persist the active reservation atomically so concurrent confirmations cannot exceed capacity.
- [X] T020 [US2] Implement the Streamlit customer booking flow in `src/cathotel/web.py`; prevent selecting dates before facility-local today, omit room listing/type selection and staff controls, collect required cat fields and optional bath/massage/claw-trimming/premium-food choices, call services, and display availability, validation, conflict, or confirmation results.

**Checkpoint**: Customers can complete or safely fail the booking journey without login; successful bookings immediately consume capacity.

---

## Phase 5: User Story 3 - Retrieve or Cancel a Reservation (Priority: P3)

**Goal**: Customers use the reservation code alone to view their reservation or cancel it before the specified cutoff.

**Independent Test**: Retrieve an active booking with its valid `NNN-NNN` code, cancel it on the final permitted calendar date in `HOTEL_TIMEZONE`, and verify that an expired cancellation is refused and only a successful cancellation releases capacity.

### Tests for User Story 3

- [X] T021 [P] [US3] Add reservation-service tests for valid/unknown codes, active/cancelled states, end-of-local-day cutoff, late cancellation refusal, and one-time capacity release in `tests/unit/test_reservation_management.py`.
- [X] T022 [P] [US3] Add Streamlit AppTest coverage for code entry, detail display, cancellation confirmation, expired-cutoff messaging, and unknown-code behavior in `tests/acceptance/test_customer_reservation_management.py`.

### Implementation for User Story 3

- [X] T023 [US3] Implement reservation lookup by exact randomly generated six-digit `NNN-NNN` code in `src/cathotel/services/reservations.py`; treat the code as the sole customer credential and do not limit failed attempts.
- [X] T024 [US3] Implement transactional cancellation in `src/cathotel/services/reservations.py`; allow cancellation through the end of the check-in date minus two calendar days in configured `HOTEL_TIMEZONE`, refuse it afterward, and transition active to cancelled exactly once.
- [X] T025 [US3] Add reservation lookup and cancellation screens/flows to `src/cathotel/web.py`; show details and status for a recognized code, require cancellation confirmation, show unknown-code and deadline errors, provide no reservation-edit controls, and send no external notifications.

**Checkpoint**: Customers can self-manage reservation details/status and release capacity only when cancellation is permitted.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the integrated implementation and keep setup documentation accurate.

- [X] T026 [P] Update package metadata and run instructions in `README.md` for uv setup, required `.env` settings, Streamlit startup, and Typer capacity import.
- [X] T027 Run and resolve the focused unit, integration, and acceptance suite with `uv run pytest`.
- [X] T028 Validate customer and staff workflows against `specs/001-cat-room-booking/quickstart.md`; resolve failures and update the guide if actual command behavior differs.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; run first.
- **Foundational (Phase 2)**: Depends on setup; blocks all user stories.
- **US1 (Phase 3)**: Depends on foundation; prioritized first because capacity data enables availability and bookings.
- **US2 (Phase 4)**: Depends on US1 capacity records and import service.
- **US3 (Phase 5)**: Depends on US2 reservations and code generation.
- **Polish (Phase 6)**: Depends on the user stories selected for delivery.

### User Story Dependencies

- **US1 (P1)**: Starts after foundation; independently delivers staff-managed dated capacity.
- **US2 (P2)**: Starts after US1 because booking requires capacity records and availability calculations.
- **US3 (P3)**: Starts after US2 because retrieval and cancellation require created reservations.

### Parallel Opportunities

- T003 can run independently after paths exist; dependency and entry-point changes to `pyproject.toml` (T001-T004) should be applied sequentially.
- US1 tests T010-T011 can run in parallel; complete T012-T013 sequentially in the same service file, then implement CLI T014.
- US2 tests T015-T016 can run in parallel; implementation T017-T019 shares `reservations.py` and precedes UI task T020.
- US3 tests T021-T022 can run in parallel; service tasks T023-T024 precede UI task T025.
- US stories are sequential (US1 → US2 → US3) because of capacity and reservation data dependencies.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete setup and foundational tasks.
2. Add pytest and complete US1 tests, then capacity model, all-or-nothing CSV service, and Typer import.
3. Run `uv run pytest tests/unit/test_capacity_service.py tests/integration/test_capacity_cli.py` and confirm valid import, malformed input, duplicate dates, and capacity conflicts.
4. Stop for review; US1 delivers staff capacity definition, while customer booking arrives in the next increment.

### Incremental Delivery

1. Deliver US1 to establish room capacity and automated CSV-import checks.
2. Add US2 to enable customer availability checks and immediate bookings; run booking unit and acceptance tests.
3. Add US3 to enable code-based retrieval and policy-bound cancellation; run management tests.
4. Run `uv run pytest` and validate integrated flows against the quickstart guide.

## Notes

- Every task checkbox follows `- [ ] T### [P?] [Story?] Description with exact file path`.
- `[P]` is used only for tests in distinct files that can be authored independently.
- Tests are included as part of the approved validation approach; pytest is a uv development dependency.
- All business rules belong in services; Streamlit views and Typer commands remain thin adapters.

## Phase 7: Convergence

- [X] T029 Fix capacity validation in `src/cathotel/services/capacity.py` to count every active reservation occupying each imported date (arrival-inclusive, departure-exclusive), not only reservations arriving on that date; add an overlapping-stay capacity-reduction regression test in `tests/unit/test_capacity_service.py` per FR-013 and US1/AC3 (contradicts, CRITICAL).
- [X] T030 Require capacity CSV dates to match exact `YYYY-MM-DD` format before parsing in `src/cathotel/services/capacity.py`; add a test that rejects compact dates such as `20300101` in `tests/unit/test_capacity_service.py` per plan: CSV date format (partial, MEDIUM).
