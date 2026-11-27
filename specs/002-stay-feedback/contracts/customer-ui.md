# Customer UI Contract: Stay Feedback

Extends the "Manage reservation" page of feature 001. Shown below the
reservation details after a successful code lookup.

| Reservation state | What the customer sees |
|---|---|
| Cancelled | Existing cancelled message; no feedback section |
| Active, stay not ended (today < departure) | Info: "Feedback opens on your departure date (YYYY-MM-DD)." plus existing cancellation controls |
| Active, stay ended, no feedback | Subheader "How was your cat's stay?"; form `feedback_form` with radio "Rating (1 = poor, 5 = excellent)" options 1–5 and no default, text area "Short review (optional)" max 500 chars, submit button "Send feedback". No cancellation controls (deadline has passed) |
| Active, stay ended, feedback exists | Success "Thank you for your feedback!", "Your rating: N/5", and the review if any |

Errors (shown with `st.error`, nothing saved):

- No rating selected → "Please choose a rating from 1 to 5."
- Review too long → "Review must be at most 500 characters."
- Already submitted → "Feedback was already submitted for this reservation."
