# Tasks: Customer Stay Feedback

**Input**: Design documents from `/specs/002-stay-feedback/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, and `contracts/`

**Organization**: Customer feedback submission (P1), then staff feedback listing (P2). Each story has focused automated tests before its implementation.

## Phase 1: Setup

No new dependencies or entry points are needed; feature 001 setup is reused.

---

## Phase 2: Foundational (Blocking Prerequisites)

- [X] T001 Define the `Feedback` SQLModel in `src/cathotel/models.py` per `data-model.md` `Feedback.id`, `Feedback.reservation_id` (unique FK to `reservation.id`), `Feedback.rating` (CHECK 1–5), `Feedback.review` (nullable, ≤ 500), and `Feedback.created_at`.

**Checkpoint**: `create_all` creates the `feedback` table in new and existing databases.

---

## Phase 3: User Story 1 - Leave Feedback After a Stay (Priority: P1) 🎯 MVP

**Goal**: A customer with an ended, active reservation can submit one rating and optional review via the reservation-code lookup.

**Independent Test**: Seed a completed reservation, submit feedback through the Manage reservation page, and verify it is stored and shown on later lookups.

### Tests for User Story 1

- [X] T002 [P] [US1] Add service tests in `tests/unit/test_feedback_service.py`: eligibility (ended vs. future vs. departure day vs. cancelled), rating 1–5 bounds, missing rating, whitespace-only review stored as none, review > 500 chars rejected, second submission rejected, unknown code rejected.
- [X] T003 [P] [US1] Add AppTest acceptance tests in `tests/acceptance/test_customer_feedback.py`: submit flow with thank-you message, missing-rating error, already-reviewed reservation shows feedback without a form, future reservation shows the "feedback opens" info and no form.

### Implementation for User Story 1

- [X] T004 [US1] Implement `src/cathotel/services/feedback.py`: `FeedbackError`, `can_leave_feedback(reservation, today)`, `get_feedback(session, reservation)`, and `submit_feedback(session, code, rating, review, *, hotel_timezone, today=None)` enforcing FR-002–FR-005 and mapping a concurrent unique-constraint violation to "already submitted".
- [X] T005 [US1] Add the feedback section to `manage_reservation()` in `src/cathotel/web.py` per `contracts/customer-ui.md`, calling only `services/feedback.py`; hide cancellation controls once the stay has ended.

**Checkpoint**: Customers can submit and see their feedback; ineligible reservations show no form.

---

## Phase 4: User Story 2 - Review Customer Feedback (Priority: P2)

**Goal**: Staff list all feedback and the average rating from the CLI.

**Independent Test**: Seed feedback, run `cathotel feedback list`, and verify entries, ordering, and summary; verify the empty state.

### Tests for User Story 2

- [X] T006 [P] [US2] Add CliRunner tests in `tests/integration/test_feedback_cli.py` for listed entries (newest first, review line optional), summary count and average to one decimal, and the "No feedback yet." empty state.

### Implementation for User Story 2

- [X] T007 [US2] Add `list_feedback(session)` returning entries with their reservations newest first, and `average_rating(entries)` in `src/cathotel/services/feedback.py`.
- [X] T008 [US2] Add the Typer `feedback list` command in `src/cathotel/cli.py` per `contracts/staff-cli.md`.

**Checkpoint**: Staff can read all feedback without touching the customer web app.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T009 Document the feedback form and `cathotel feedback list` in `README.md`.
- [X] T010 Run `uv run pytest` and review changes against the constitution (logic in services, staff listing CLI-only, comments explain why only).

## Dependencies

- T001 blocks all story tasks.
- US1 (T002–T005) before US2 (T006–T008): staff listing needs stored feedback.
- T009–T010 last.

## Parallel Opportunities

- T002 and T003 (different test files); T006 alongside US1 implementation once T001 is done.

## Implementation Strategy

MVP = Phase 2 + US1. US2 adds the staff view; Polish closes out.
