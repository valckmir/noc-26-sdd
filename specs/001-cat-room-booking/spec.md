# Feature Specification: Cat Room Booking

**Feature Branch**: `001-cat-room-booking`

**Created**: 2026-11-17

**Status**: Draft

**Input**: User description: "Develop a web application for cat owner to let them book rooms for cats. Customers must be able to pick a date range. There is only one type of rooms, therefore there is no need for room listing and room type selection. If there is any room available, customers are prompted to add cat name, breed, social or not, and daily walks required. Customers can select optional wellness (bath, massage, claws trimming) and premium cat food. Room availability/capacity is provided by staff by uploading CSV with date and room capacity. Entire process is accountless - no registrations and logins are supported. After confirming and sending reservation request, the app generates unique reservation code. This code is used to show reservation details or cancel it. Modifications are not allowed. Reservations are effective immediately - no human confirmation is required. No notification is sent; all information is shown only in the application."

## Clarifications

### Session 2026-11-17

- Q: What accountless access should protect staff capacity uploads from customers and other unauthorized visitors? → A: The web application is for customers only; staff uses a different type of access to the system.
- Q: Should the system limit repeated failed attempts to use reservation codes? → A: No; a unique reservation code alone is sufficient, with no limit on failed attempts.
- Q: Should the booking interface permit selecting past dates? → A: No; the UI must not allow selection of past dates.
- Q: May a customer cancel through the end of the calendar day that is two days before check-in? → A: Yes; cancellation is allowed through the end of the local calendar day two days before check-in.
- Q: What format must reservation codes use? → A: Six digits split into two three-digit groups separated by a hyphen (###-###).
- Q: Should the six-digit code be split into two groups of three digits (###-###)? → A: Yes; use two groups of three digits (###-###).
- Q: How should reservation codes be generated? → A: Generate a random six-digit number, displayed in two three-digit groups separated by a hyphen, and ensure it is unique.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Provide Room Capacity (Priority: P1)

As a staff member using the separate staff access path, I want to upload a CSV
of dated room capacities, so that customers can book only against the capacity
available for each night.

**Why this priority**: Staff-defined capacity is the foundation for reliable
availability checks and must be established before customers can book.

**Independent Test**: Run the staff CLI with a valid CSV and verify each listed
date and room capacity is stored in SQLite. Then submit malformed, duplicate-date,
or reservation-conflicting data and verify the import fails and the database
remains unchanged.

**Acceptance Scenarios**:

1. **Given** a valid CSV with a date and non-negative room capacity on each row,
   **When** staff upload it, **Then** the capacity for each listed date is
   updated and the result is shown in the application.
2. **Given** a CSV with missing columns, invalid dates, negative or non-numeric
   capacity, or duplicate dates, **When** staff upload it, **Then** the upload is
   rejected with a useful error and no rows from that upload are applied.
3. **Given** staff update capacity for dates that have active reservations,
   **When** an update would make any date's capacity lower than its active
   reservations, **Then** that update is rejected and existing capacity remains
   unchanged.
4. **Given** a customer checks dates for which no capacity has been provided,
   **When** availability is evaluated, **Then** those dates are treated as
   unavailable.

---

### User Story 2 - Book a Cat's Stay (Priority: P2)

As a cat owner, I want to check availability for a date range and submit the
stay and service details, so that I can immediately secure an available room
without creating an account or waiting for staff approval.

**Why this priority**: Booking is the primary customer value, enabled by staff
first defining room capacity.

**Independent Test**: Provide available capacity for a date range, complete the
booking flow, and verify that the customer receives a reservation code and
immediate confirmation with the submitted details.

**Acceptance Scenarios**:

1. **Given** capacity is available for every night in a valid date range,
   **When** a customer selects the range, enters the cat's required details,
   selects any optional services, and confirms the booking, **Then** the
   reservation is immediately confirmed and a unique reservation code in the
   format ###-### and reservation details are shown.
2. **Given** the customer is checking a range that has no room available on at
   least one night, **When** availability is checked, **Then** the customer is
   told the range cannot be booked and is not prompted to submit a reservation.
3. **Given** the customer has not supplied all required cat details,
   **When** they attempt to confirm, **Then** the missing or invalid details are
   identified and no reservation is created.
4. **Given** another customer books the last available room while this customer
   is completing the form, **When** this customer confirms, **Then** the system
   does not exceed capacity and explains that the range is no longer available.
5. **Given** a customer is choosing stay dates, **When** they view past dates in
   the date-selection controls, **Then** those dates cannot be selected.

---

### User Story 3 - Retrieve or Cancel a Reservation (Priority: P3)

As a cat owner with a reservation code, I want to view my reservation or cancel
it, so that I can manage the stay without an account or contacting staff.

**Why this priority**: Customers need a self-service way to verify their booking
and release capacity if their plans change, after the capacity and booking
workflows are available.

**Independent Test**: Use a valid reservation code to retrieve the reservation,
then cancel it and verify that it is no longer active and its capacity is
available for a new booking.

**Acceptance Scenarios**:

1. **Given** an active reservation, **When** the customer submits its valid
   reservation code, **Then** the reservation details and current status are
   shown.
2. **Given** an active reservation and the current local calendar date is no
   later than two calendar days before check-in, **When** the customer confirms
   cancellation using its valid code, **Then** the reservation is cancelled and
   the cancellation is shown in the application.
3. **Given** an active reservation and the current local calendar date is later
   than two calendar days before check-in, **When** the customer attempts to
   cancel it, **Then** cancellation is refused and the reservation remains active.
4. **Given** a reservation has been cancelled, **When** a customer checks
   availability for its dates, **Then** the cancelled reservation no longer
   consumes room capacity.
5. **Given** an invalid or unknown reservation code, **When** submitted,
   **Then** no reservation details are disclosed and the customer receives a
   clear message that the code could not be used.
6. **Given** a reservation is already cancelled, **When** its code is used to
   view or cancel it again, **Then** its cancelled status is shown and no
   additional capacity is released.

---

### Edge Cases

- A requested range must have a departure date after its arrival date; same-day
  and reversed ranges cannot be booked. Past dates cannot be selected for a stay.
- A range is available only when every night in it has capacity remaining.
- The arrival date is included and the departure date is excluded from occupied
  nights, following the common overnight-stay convention.
- A CSV upload is rejected as a whole if any row is invalid; valid rows are not
  partially applied.
- Capacity cannot be reduced below the count of active reservations on any
  affected date.
- Booking confirmation rechecks capacity so concurrent attempts cannot
  overbook a date.
- A reservation code must be a randomly generated six-digit number, unique and
  displayed as two three-digit groups separated by a hyphen (###-###). Cancelled
  reservations remain identifiable as cancelled and do not consume capacity. The
  code alone authorizes retrieval and cancellation; repeated failed code
  attempts are not limited.
- Cancellation is allowed through the end of the local calendar day that is two
  calendar days before check-in. On the following day, cancellation is no longer
  allowed.
- Optional services may be selected independently, including any combination
  of wellness treatments and premium cat food.
- Empty or whitespace-only cat name or breed values are invalid.
- No email, text, or other external notification is sent; booking, retrieval,
  cancellation, and upload results are communicated in the application.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST let a customer select an arrival date and a later
  departure date without selecting a room or room type. The customer-facing date
  controls MUST NOT allow dates before the current calendar date to be selected.
- **FR-002**: The system MUST determine availability for the full stay using the
  room capacity and active reservations for each occupied night.
- **FR-003**: The system MUST treat the arrival date as occupied and the
  departure date as not occupied; dates lacking supplied capacity MUST be
  unavailable.
- **FR-004**: The system MUST collect a cat name, breed, social status, and
  whether daily walks are required before a customer can confirm a reservation.
- **FR-005**: The system MUST let customers independently choose bath, massage,
  claw trimming, and premium cat food as optional services.
- **FR-006**: The system MUST recheck availability when a reservation is
  confirmed and MUST NOT allow active reservations to exceed capacity on any
  occupied date.
- **FR-007**: On successful confirmation, the system MUST make the reservation
  effective immediately and show its details and a unique reservation code in
  the format ###-### in the application, without requiring staff approval. Each
  code MUST be generated randomly, contain exactly six digits divided into two
  three-digit groups by one hyphen, and MUST be unique.
- **FR-008**: The system MUST let a customer retrieve reservation details by
  providing its reservation code, without registration or login.
- **FR-009**: The system MUST let a customer cancel an active reservation using
  its reservation code through the end of the local calendar day two calendar
  days before check-in, and show the cancellation result in the application.
  After that deadline, the system MUST refuse cancellation and keep the
  reservation active.
- **FR-010**: The system MUST NOT allow reservation details to be modified after
  confirmation. Customers who need different details may cancel and make a new
  reservation only before the cancellation deadline, subject to availability.
- **FR-016**: A unique reservation code MUST be sufficient to retrieve or cancel
  its reservation. The system MUST NOT require additional customer credentials
  or limit repeated failed reservation-code attempts.
- **FR-011**: Through the separate staff access path, the system MUST validate
  uploaded capacity data as a CSV with date and room capacity columns, reject
  invalid or duplicate-date data as a whole, and explain upload errors.
- **FR-012**: Staff MUST be able to update capacity for dates included in a valid
  upload through the staff access path; dates not included in that upload MUST
  retain their existing capacity. The customer-facing web application MUST NOT
  expose staff capacity-upload functionality.
- **FR-013**: The system MUST reject a capacity update that would put any
  affected date below its active reservation count, without partially applying
  that upload.
- **FR-014**: The system MUST communicate booking, reservation lookup,
  cancellation, and capacity-upload outcomes in the application and MUST NOT
  send external notifications.
- **FR-015**: The customer reservation journey MUST NOT require account creation
  or login. The customer-facing experience MUST provide one room option and MUST
  NOT include room listing or room-type selection.

### Key Entities *(include if feature involves data)*

- **Capacity date**: A calendar date and the total number of rooms available
  that night, supplied by staff.
- **Reservation**: A confirmed stay identified by a unique randomly generated
  six-digit code displayed as two three-digit groups separated by a hyphen
  (###-###), arrival and departure dates, cat details, selected optional
  services, and an active or cancelled status.
- **Cat details**: The cat's name, breed, social status, and daily-walk
  requirement associated with a reservation.
- **Optional service selection**: The set of wellness treatments and food
  options associated with a reservation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In acceptance testing, every successfully confirmed reservation
  has a unique code, and no tested date exceeds its supplied room capacity.
- **SC-002**: All tested malformed, duplicate-date, or capacity-conflicting CSV
  uploads are rejected without applying any part of the upload, and the staff
  member can identify the cause from the displayed result.
- **SC-003**: Customers receive booking, lookup, and cancellation outcomes in
  the application with no external notification sent.

## Assumptions

- A stay occupies each night from arrival through the night before departure;
  arrival and departure dates follow the common check-in/check-out convention.
- Room capacities are non-negative whole numbers. A valid upload updates only
  dates listed in that file; dates omitted from an upload keep their previous
  capacity. Duplicate dates make the entire upload invalid.
- Each active reservation consumes one room for each occupied night, regardless
  of cat count; one reservation describes one cat.
- The unique reservation code is the sole customer credential for viewing or
  cancelling a reservation. The application does not provide customer accounts
  or limit repeated failed reservation-code attempts.
- The customer-facing web application is for customers; staff manages capacity
  through a different access path to the system. The details of that staff access
  path are outside this feature specification.
- No payment, pricing, reservation edits, waitlist, or external notifications
  are included because they were not requested.
