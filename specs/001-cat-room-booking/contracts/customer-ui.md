# Customer UI Contract

The Streamlit interface is customer-only. It does not expose staff capacity
management and does not require customer registration or login.

## Booking

1. Let the customer choose arrival and departure dates; dates before the current
   facility-local date cannot be selected.
2. Do not present room listing or room-type selection.
3. Check availability for every occupied night. Missing capacity is unavailable.
4. If unavailable, explain that the requested range cannot be booked and do not
   proceed to reservation details.
5. If available, collect cat name, breed, social status, daily-walk requirement,
   and optional bath, massage, claw trimming, and premium cat food choices.
6. On confirmation, recheck capacity. On success show the immediate confirmation,
   submitted details, and unique reservation code formatted `NNN-NNN`. On conflict,
   explain that availability changed and do not overbook.

## Reservation lookup and cancellation

- Accept the six-digit reservation code formatted `NNN-NNN` as the sole customer
  credential. Show no reservation data for an unknown code.
- Show current details and status for a recognized code.
- Allow cancellation through the end of the facility-local calendar date two
  calendar days before check-in. After this date, refuse cancellation and explain
  that the cancellation deadline has passed.
- Do not offer post-confirmation edits. A customer can cancel and create a new
  reservation only while cancellation is permitted and subject to availability.
- Show all outcomes in the interface; send no external notifications.
