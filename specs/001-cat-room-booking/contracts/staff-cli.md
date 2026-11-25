# Staff CLI Contract

Staff capacity management is provided through a Typer command-line interface,
not through the customer web UI. The CLI uses the same configured SQLite
 database and capacity service as the customer application.

## Capacity import

Proposed command form:

```text
cathotel capacity import PATH
```

Input is a UTF-8 CSV with exactly these headers:

```csv
date,room_capacity
2026-12-01,8
```

- `date` uses ISO `YYYY-MM-DD` format.
- `room_capacity` is a non-negative whole number.
- Each date may occur once per file.
- Dates in a successful file are inserted or updated; omitted dates are
  unchanged.
- Validate all rows and capacity constraints before applying changes.
- Reject an invalid file or a capacity below existing active reservations
  without applying any part of the file.
- Report the number of dates updated on success; report actionable row/header
  errors on failure.
- The command exits successfully only when the complete import succeeds and
  returns a non-zero exit status on validation or persistence failure.

The CLI accepts the application configuration (including the SQLite database
path) from Pydantic Settings and `.env`. The operating environment is
responsible for allowing only staff to invoke the command.
