# Staff CLI Contract: Feedback

```text
cathotel feedback list
```

Uses the same settings and SQLite database as the rest of the CLI.

Output, newest first, one block per entry:

```text
2026-11-30  123-456  stay 2026-11-20 to 2026-11-25  rating 5/5
  Lovely staff, Mimi came back happy.
```

Entries without a review omit the indented line. After the entries:

```text
3 feedback entries, average rating 4.3/5
```

With no feedback: `No feedback yet.` Exit status 0 in both cases; non-zero with
an error message on configuration or database failure.
