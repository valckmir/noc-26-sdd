# Implementation Plan: Customer Stay Feedback

**Branch**: `002-stay-feedback` | **Date**: 2026-11-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-stay-feedback/spec.md`

## Summary

Customers whose stay has ended can rate it (1–5) and leave an optional short
review from the existing "Manage reservation" page, once per reservation. Staff
read all feedback and the average rating with a new `cathotel feedback list`
CLI command. A new `Feedback` table linked one-to-one to `Reservation` stores
the data; all rules live in a new `services/feedback.py`.

## Technical Context

**Language/Version**: Python 3.13 (uv)

**Primary Dependencies**: Streamlit, Typer, SQLModel, Pydantic Settings (unchanged; no new dependencies)

**Storage**: Existing SQLite database; one new table `feedback`

**Testing**: pytest; Streamlit `AppTest` for the customer flow; Typer `CliRunner` for the staff command

**Target Platform**: Same single host as feature 001

**Project Type**: Streamlit web app + Typer CLI, single package `src/cathotel`

**Performance Goals**: Not performance-sensitive (one row per completed stay)

**Constraints**: One feedback per reservation enforced by the database; eligibility uses `HOTEL_TIMEZONE`

**Scale/Scope**: One new model, one service module, one UI section, one CLI command

## Constitution Check

| Principle | Check | Status |
|-----------|-------|--------|
| I. Customer-Centered Simplicity | Feedback form serves customers; feedback list serves staff, who need it to act on the feedback. No extra features (no replies, edits, public ratings) | PASS |
| II. Layered Business Logic | Eligibility, validation, uniqueness, and averages live in `services/feedback.py`; `web.py` and `cli.py` only collect input and render results | PASS |
| III. Simplicity Over Complexity | One table with a unique FK, `create_all` creates it, no migration tool, no new dependency | PASS |
| IV. Role-Aware Experiences | Customer submits via code lookup only; listing is CLI-only and absent from the web app | PASS |
| V. Intentional Code Comments | Comments only where a rule is non-obvious (e.g. why departure day counts as stay end) | PASS |

Post-design re-check: PASS (see data-model.md and contracts/).

## Project Structure

### Documentation (this feature)

```text
specs/002-stay-feedback/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── customer-ui.md
│   └── staff-cli.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/cathotel/
├── models.py              # + Feedback model
├── services/feedback.py   # new: eligibility, submit, lookup, list/summary
├── web.py                 # + feedback section in manage_reservation()
└── cli.py                 # + `feedback list` command
tests/
├── unit/test_feedback_service.py
├── acceptance/test_customer_feedback.py
└── integration/test_feedback_cli.py
```

**Structure Decision**: Extend the existing single package; follow the
`services/<area>.py` pattern of feature 001.

## Complexity Tracking

No violations. Nothing to justify.
