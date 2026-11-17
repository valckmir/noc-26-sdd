# Tasks: Cat Room Booking

**Input**: Design documents from `/specs/001-cat-room-booking/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, and `contracts/`

**Organization**: Tasks are grouped by the prioritized user stories: staff capacity definition (P1), customer booking (P2), then reservation lookup/cancellation (P3). Test tasks are omitted because TDD was not requested.

## Phase 1: Setup

**Purpose**: Establish the Python package dependencies and runnable entry points.

- [ ] T001 Add Streamlit, Typer, SQLModel, and Pydantic Settings dependencies in `pyproject.toml`, preserving the existing Python 3.13 and uv configuration.
- [ ] T002 [P] Create service package initializer in `src/cathotel/services/__init__.py`.
- [ ] T003 Add or update the `cathotel` console entry point for the Typer CLI in `pyproject.toml`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Provide shared configuration, database initialization, and core domain models required by every story.

- [ ] T004 Implement Pydantic Settings loading `.env`, SQLite database path, and required IANA `HOTEL_TIMEZONE` in `src/cathotel/config.py`.
- [ ] T005 Implement SQLModel SQLite engine, session creation, and table initialization helpers in `src/cathotel/database.py`.
- [ ] T006 Define the `CapacityDate` SQLModel in `src/cathotel/models.py` with `date` as the unique primary/business key and `room_capacity` as a required non-negative integer.
- [ ] T007 Define the `Reservation` SQLModel in `src/cathotel/models.py` with a unique six-digit code displayed as two three-digit groups, arrival/departure dates, non-empty trimmed cat name and breed, required social and daily-walk booleans, four optional service booleans defaulting false, active/cancelled status defaulting active, and creation timestamp.
- [ ] T008 Implement shared facility-local date and cancellation-cutoff helpers in `src/cathotel/services/dates.py`, using configured `HOTEL_TIMEZONE` and cutoff through the end of the local date two calendar days before check-in.

**Checkpoint**: Shared settings, SQLite session, domain models, and date rules are available before story work.

---

## Phase 3: User Story 1 - Provide Room Capacity (Priority: P1) 🎯 MVP

**Goal**: Staff can import dated room capacities via the Typer CLI, with strict all-or-nothing validation and no customer-facing staff tools.

**Independent Test**: Invoke the CLI with a valid CSV and verify listed capacities are stored; submit malformed, duplicate-date, or reservation-conflicting input and verify the command fails without changing any capacity.

- [ ] T009 [US1] Implement CSV parsing and validation in `src/cathotel/services/capacity.py`; require exactly `date,room_capacity`, ISO `YYYY-MM-DD`, non-negative whole-number capacities, and no duplicate date per file; reject the complete file if any row is invalid.
- [ ] T010 [US1] Implement transactional capacity upsert in `src/cathotel/services/capacity.py`; update only dates present in the import, leave omitted dates unchanged, and reject the entire update if any new capacity is below its active reservation count.
- [ ] T011 [US1] Implement the Typer `capacity import PATH` command in `src/cathotel/cli.py` using shared settings, SQLite sessions, and capacity service; report successful row count or actionable errors, return non-zero on failure, and keep staff upload controls out of `src/cathotel/web.py`.

**Checkpoint**: The staff CLI can define capacity and reject invalid updates atomically; customer UI remains separate.

---

## Phase 4: User Story 2 - Book a Cat's Stay (Priority: P2)

**Goal**: Customers select an allowed date range, see availability, enter required cat details and optional services, and immediately receive a reservation code when confirmed.

**Independent Test**: With capacity loaded, book an available stay and verify immediate confirmation with a unique `NNN-NNN` code; verify unavailable dates, invalid details, past dates, and competing last-room bookings cannot create an invalid or over-capacity reservation.

- [ ] T012 [US2] Implement reservation-code generation and uniqueness retry in `src/cathotel/services/reservations.py`; generate exactly six numeric digits, preserve leading zeros, display as `NNN-NNN`, and enforce uniqueness in SQLite.
- [ ] T013 [US2] Implement service-level date/detail validation and availability checks in `src/cathotel/services/reservations.py`; reject past arrival dates, require departure after arrival, count occupied nights as arrival-inclusive/departure-exclusive, require capacity on every occupied night, and treat dates without capacity as unavailable.
- [ ] T014 [US2] Implement transactional reservation confirmation in `src/cathotel/services/reservations.py`; recheck every occupied night's capacity and persist the active reservation atomically so concurrent confirmations cannot exceed capacity.
- [ ] T015 [US2] Implement the Streamlit customer booking flow in `src/cathotel/web.py`; prevent selecting dates before facility-local today, omit room listing/type selection and staff controls, collect required cat fields and optional bath/massage/claw-trimming/premium-food choices, call services, and display availability, validation, conflict, or confirmation results.

**Checkpoint**: Customers can complete or safely fail the booking journey without login; successful bookings immediately consume capacity.

---

## Phase 5: User Story 3 - Retrieve or Cancel a Reservation (Priority: P3)

**Goal**: Customers use the reservation code alone to view their reservation or cancel it before the specified cutoff.

**Independent Test**: Retrieve an active booking with its valid `NNN-NNN` code, cancel it on the final permitted local calendar date, and verify that an expired cancellation is refused and only a successful cancellation releases capacity.

- [ ] T016 [US3] Implement reservation lookup by exact six-digit `NNN-NNN` code in `src/cathotel/services/reservations.py`; treat the code as the sole customer credential and do not limit failed attempts.
- [ ] T017 [US3] Implement transactional cancellation in `src/cathotel/services/reservations.py`; allow cancellation through the end of facility-local check-in date minus two calendar days, refuse it afterward, and transition active to cancelled exactly once.
- [ ] T018 [US3] Add reservation lookup and cancellation screens/flows to `src/cathotel/web.py`; show details and status for a recognized code, require cancellation confirmation, show unknown-code and deadline errors, and send no external notifications.

**Checkpoint**: Customers can self-manage reservation details/status and release capacity only when cancellation is permitted.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the integrated implementation and keep setup documentation accurate.

- [ ] T019 [P] Update package metadata and run instructions in `README.md` for uv setup, required `.env` settings, Streamlit startup, and Typer capacity import.
- [ ] T020 Validate the customer and staff workflows against `specs/001-cat-room-booking/quickstart.md`; resolve failures and update the guide if actual command behavior differs.

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

- T002 can run independently of the dependency edit in T001; T003 also edits `pyproject.toml` and follows T001.
- US1 parsing/validation and transactional persistence (T009-T010) are in the same service file and should be completed sequentially; CLI integration T011 follows them.
- In US2, T012-T014 share `reservations.py` and are sequential; the UI task T015 follows service behavior.
- In US3, T016-T017 share `reservations.py` and are sequential; UI task T018 follows them.
- US stories are sequential (US1 → US2 → US3) because their capacity and reservation data dependencies are real.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete setup and foundational tasks.
2. Complete US1 capacity model, all-or-nothing CSV service, and Typer import.
3. Manually validate valid import, malformed input, duplicate dates, and capacity conflicts.
4. Stop for review; US1 delivers staff capacity definition, while customer booking arrives in the next increment.

### Incremental Delivery

1. Deliver US1 to establish room capacity.
2. Add US2 to enable customer availability checks and immediate bookings.
3. Add US3 to enable code-based retrieval and policy-bound cancellation.
4. Validate integrated flows against the quickstart guide.

## Notes

- Every task checkbox follows `- [ ] T### [P?] [Story?] Description with exact file path`.
- `[P]` is used only for tasks with separable files and no incomplete-task dependency.
- Tests are not separate tasks because neither TDD nor test implementation was explicitly requested.
- All business rules belong in services; Streamlit views and Typer commands remain thin adapters.
