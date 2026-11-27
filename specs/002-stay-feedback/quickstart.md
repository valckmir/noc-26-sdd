# Quickstart: Customer Stay Feedback

## Setup

Same as feature 001: `uv sync`, copy `.env.example` to `.env`.

## Validate as customer

1. Create a reservation whose departure date is today or earlier (for example
   via the unit-test helpers or by booking and then adjusting the database).
2. `uv run streamlit run src/cathotel/web.py` → "Manage reservation" → enter
   the code.
3. Submit without a rating → error, nothing saved.
4. Choose a rating, write a review, submit → thank-you message with rating.
5. Look the code up again → feedback shown, no form.
6. Look up a future or cancelled reservation → no form (see
   [contracts/customer-ui.md](contracts/customer-ui.md)).

## Validate as staff

```sh
uv run cathotel feedback list
```

Expected output per [contracts/staff-cli.md](contracts/staff-cli.md).

## Automated tests

```sh
uv run pytest
```
