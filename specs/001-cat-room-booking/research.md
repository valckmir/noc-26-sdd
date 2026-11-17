# Research: Cat Room Booking

## Decision: Use the requested Python application stack

**Decision**: Build the customer web interface with Streamlit, staff CSV import
with Typer, business/persistence models with SQLModel, SQLite storage, Pydantic
Settings for configuration, and uv for dependency management.

**Rationale**: These are explicit project constraints. A single Python package
keeps deployment and maintenance simple while serving the two distinct access
surfaces.

**Alternatives considered**: A separate web API/frontend, a staff web console,
and a server database. These are unnecessary for the stated single-facility
scope and were not requested.

## Decision: Keep business behavior in services

**Decision**: Streamlit pages and Typer command functions delegate all capacity,
booking, validation, code generation, and cancellation behavior to services.

**Rationale**: This enforces the constitution's service-layer rule and enables
shared behavior across both entry points.

**Alternatives considered**: Placing rules in UI callbacks or CLI handlers was
rejected because it duplicates and obscures business logic.

## Decision: Make booking capacity checks and reservation creation atomic

**Decision**: The reservation service performs availability revalidation and
reservation insertion in one SQLite transaction. Enforce the reservation-code
unique constraint in storage and retry code generation on collision. CSV import
validates all rows and capacity/reservation constraints before applying all
updates in a transaction.

**Rationale**: UI-level availability is only advisory; two customers can
otherwise book the last room simultaneously. Atomic operations prevent
partial imports and overbooking.

**Alternatives considered**: Checking availability before a separate insert, or
committing CSV rows incrementally, was rejected because either can leave
inconsistent capacity.

## Decision: Interpret booking and cancellation dates in the facility timezone

**Decision**: Require `HOTEL_TIMEZONE` as an IANA time-zone setting. Disallow
past arrival dates in both the customer interface and service validation. A
cancellation remains permitted through the end of the local calendar day two
days before check-in.

**Rationale**: The specification defines calendar-day behavior and prohibits
past date selection. Using one configured facility timezone keeps UI limits and
cancellation cutoffs consistent.

**Alternatives considered**: Using the server's implicit timezone or converting
the cutoff to a rolling 48-hour interval was rejected because results would vary
by host or conflict with calendar-day semantics.

## Decision: Use a six-digit code with the specified display grouping

**Decision**: Generate a six-digit numeric code, display and accept it as
`NNN-NNN`, enforce uniqueness, and treat the code as the sole customer
credential. Do not limit failed code attempts, as clarified by the user.

**Rationale**: This implements the specified format and accountless retrieval
and cancellation behavior. A database uniqueness constraint is required because
the possible code space is finite.

**Alternatives considered**: Longer opaque tokens and additional customer
credentials conflict with the explicit requirements.

## Decision: Define an explicit capacity CSV header

**Decision**: Require a UTF-8 CSV with exactly the columns `date,room_capacity`,
using ISO `YYYY-MM-DD` dates and non-negative whole-number capacities. Treat
duplicate dates or any malformed row as a failure of the complete import.

**Rationale**: Canonical field names and a date representation make imports
predictable and validation errors actionable. The two-column format and
all-or-nothing behavior follow the feature requirements.

**Alternatives considered**: Guessing column aliases or accepting ambiguous
date formats was rejected to keep the staff workflow simple and deterministic.

## Decision: Keep configuration explicit and deployment-neutral

**Decision**: Use a Pydantic Settings model with `.env` support for the SQLite
path and required `HOTEL_TIMEZONE`. Do not commit secrets or environment-specific
configuration.

**Rationale**: The user selected Pydantic Settings and `.env`; explicit timezone
configuration is needed for correct calendar rules.

**Alternatives considered**: Hard-coded database paths/timezones and a separate
configuration framework were rejected as brittle or unnecessary.

## Planning assumptions and targets

- The initial service is for one facility and a modest booking volume; no
  multi-site partitioning or external services are required.
- Initial CSV imports are expected to contain no more than 10,000 rows. The
  planning target is under 2 seconds p95 for ordinary customer operations and
  imports at this size, excluding app startup; confirm under deployment
  conditions.
- The CLI runs in an environment with access to the same SQLite database file
  used by the customer application.
- Staff CLI invocation permissions are provided by the operating environment;
  designing a separate staff authentication system is outside this feature.
