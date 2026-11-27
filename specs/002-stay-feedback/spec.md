# Feature Specification: Customer Stay Feedback

**Feature Branch**: `002-stay-feedback`

**Created**: 2026-11-27

**Status**: Draft

**Input**: User description: "Feature Request: Customer Stay Feedback Form (issue #1). To better understand and improve customer satisfaction, we need to provide customers with a feedback form. The form should allow them to rate their experience and provide a short written review of the services received."

## Clarifications

### Session 2026-11-27

- Q: How does an accountless customer reach the feedback form? → A: Through the existing reservation-code lookup ("Manage reservation"); the code is the only proof of the stay.
- Q: When may feedback be submitted? → A: Only for an active (not cancelled) reservation once the stay has ended, i.e. the facility-local date is on or after the departure date.
- Q: How many times may a reservation be reviewed, and can feedback be changed? → A: Once per reservation; feedback is final, consistent with the rule that reservations cannot be modified.
- Q: What rating scale is used? → A: A required whole-number rating from 1 (poor) to 5 (excellent).
- Q: Is the written review required, and how long may it be? → A: Optional; at most 500 characters after trimming whitespace.
- Q: How do staff read the feedback? → A: Through the staff CLI (`cathotel feedback list`), never through the customer web application.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Leave Feedback After a Stay (Priority: P1)

As a cat owner whose cat's stay has ended, I want to rate my experience and
write a short review using my reservation code, so that the hotel learns how
satisfied I was with the services my cat received.

**Why this priority**: Collecting feedback is the core value of the feature;
without it there is nothing for staff to read.

**Independent Test**: Seed a completed, active reservation; open "Manage
reservation", look it up by code, submit a rating with a review, and verify a
thank-you message is shown and the feedback is stored for that reservation.

**Acceptance Scenarios**:

1. **Given** an active reservation whose departure date is today or earlier,
   **When** the customer looks it up by code, **Then** a feedback form with a
   1–5 rating and an optional review of up to 500 characters is shown.
2. **Given** the feedback form is shown, **When** the customer selects a rating,
   optionally writes a review, and submits, **Then** the feedback is saved and
   the customer sees a thank-you message with the submitted rating and review.
3. **Given** the customer submits without selecting a rating, **When** the form
   is sent, **Then** nothing is saved and the customer is told a rating is
   required.
4. **Given** feedback was already submitted for a reservation, **When** the
   reservation is looked up again, **Then** the submitted feedback is shown and
   no form is offered.
5. **Given** a reservation whose stay has not ended yet, **When** it is looked
   up, **Then** no feedback form is shown and the customer is told feedback
   opens on the departure date.
6. **Given** a cancelled reservation, **When** it is looked up, **Then** no
   feedback form is shown.

---

### User Story 2 - Review Customer Feedback (Priority: P2)

As a staff member using the separate staff access path, I want to list all
customer feedback with an average rating, so that I can understand customer
satisfaction and improve the services.

**Why this priority**: Feedback only improves the hotel when staff can read it,
but it depends on feedback being collected first.

**Independent Test**: Seed feedback for several reservations, run the staff CLI
list command, and verify each entry and the average rating are printed; run it
with no feedback and verify an empty-state message.

**Acceptance Scenarios**:

1. **Given** stored feedback, **When** staff run the feedback list command,
   **Then** each entry shows the reservation code, stay dates, rating, review
   (if any), and submission date, newest first, followed by the number of
   entries and the average rating to one decimal place.
2. **Given** no stored feedback, **When** staff run the command, **Then** a
   message states that there is no feedback yet and the command succeeds.

---

### Edge Cases

- Feedback submitted twice for the same reservation (for example from two
  browser tabs) results in exactly one stored feedback; the second attempt is
  told feedback was already submitted.
- A review consisting only of whitespace is stored as no review.
- A review longer than 500 characters is rejected with a clear message and
  nothing is saved.
- A rating outside 1–5 is rejected even if it bypasses the form.
- An unknown or malformed reservation code reveals nothing, exactly as the
  existing lookup does.
- The departure day itself counts as the end of the stay in the facility's
  configured timezone (`HOTEL_TIMEZONE`).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Customers MUST be able to reach the feedback form only through
  the existing reservation-code lookup; no account or login is introduced.
- **FR-002**: The system MUST accept feedback only for an active reservation
  whose departure date is on or before the facility-local current date.
- **FR-003**: Feedback MUST contain a required whole-number rating from 1 to 5.
- **FR-004**: Feedback MAY contain a written review of at most 500 characters
  after trimming surrounding whitespace; an empty review is stored as none.
- **FR-005**: The system MUST store at most one feedback per reservation and
  MUST NOT allow feedback to be changed or deleted by customers.
- **FR-006**: After submission, and on any later lookup, the customer MUST see
  their submitted rating and review instead of the form.
- **FR-007**: For reservations not yet eligible, the customer MUST see why
  feedback is unavailable (stay not ended, or reservation cancelled) and no form.
- **FR-008**: Staff MUST be able to list all feedback via the staff CLI, newest
  first, with reservation code, stay dates, rating, review, submission date,
  entry count, and average rating.
- **FR-009**: The customer web application MUST NOT expose other customers'
  feedback or any staff feedback listing.
- **FR-010**: Feedback eligibility and validation rules MUST be enforced by the
  service layer, not only by the form.

### Key Entities

- **Feedback**: A customer's assessment of one completed stay. Belongs to
  exactly one reservation; holds the rating (1–5), an optional review text, and
  the submission time.
- **Reservation** (existing): Gains at most one related feedback. Its status and
  departure date decide whether feedback may be submitted.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A customer with a completed stay can submit feedback in under 1
  minute from opening "Manage reservation".
- **SC-002**: 100% of feedback attempts for ineligible reservations (cancelled,
  not yet ended, already reviewed) are refused without storing data.
- **SC-003**: Staff can see every stored feedback entry and the average rating
  with a single command.
- **SC-004**: No reservation ever has more than one stored feedback.

## Assumptions

- The reservation code is sufficient proof that the visitor stayed with the
  hotel; no further verification is added (consistent with feature 001).
- Feedback is anonymous apart from its link to the reservation; no customer
  contact data is collected.
- Staff do not reply to feedback in the application, and no notifications are
  sent, consistent with feature 001.
- Feedback has no submission deadline after the stay ends.
- Ratings are not shown publicly to other customers.
