from pathlib import Path

import typer
from sqlmodel import Session

from cathotel.config import get_settings
from cathotel.database import create_database_engine, create_db_and_tables
from cathotel.services.capacity import CapacityImportError, import_capacity_csv
from cathotel.services.feedback import average_rating, list_feedback

app = typer.Typer()
capacity_app = typer.Typer()
app.add_typer(capacity_app, name="capacity")
feedback_app = typer.Typer()
app.add_typer(feedback_app, name="feedback")


@app.callback()
def main() -> None:
    pass


@capacity_app.command("import")
def import_capacity(path: Path) -> None:
    """Import daily room capacities from a CSV file."""
    try:
        settings = get_settings()
        engine = create_database_engine(settings.database_path)
        create_db_and_tables(engine)
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            with Session(engine) as session:
                imported = import_capacity_csv(session, file)
    except (OSError, CapacityImportError) as error:
        typer.echo(f"Capacity import failed: {error}", err=True)
        raise typer.Exit(code=1) from error
    typer.echo(f"Imported capacity for {imported} dates.")



@feedback_app.command("list")
def list_customer_feedback() -> None:
    """List customer stay feedback, newest first, with the average rating."""
    try:
        settings = get_settings()
        engine = create_database_engine(settings.database_path)
        create_db_and_tables(engine)
        with Session(engine) as session:
            entries = list_feedback(session)
    except Exception as error:
        typer.echo(f"Feedback listing failed: {error}", err=True)
        raise typer.Exit(code=1) from error

    if not entries:
        typer.echo("No feedback yet.")
        return
    for entry in entries:
        feedback, reservation = entry.feedback, entry.reservation
        typer.echo(
            f"{feedback.created_at.date().isoformat()}  {reservation.display_code}  "
            f"stay {reservation.arrival_date.isoformat()} to "
            f"{reservation.departure_date.isoformat()}  rating {feedback.rating}/5"
        )
        if feedback.review:
            typer.echo(f"  {feedback.review}")
    noun = "entry" if len(entries) == 1 else "entries"
    typer.echo(
        f"{len(entries)} feedback {noun}, average rating {average_rating(entries):.1f}/5"
    )


if __name__ == "__main__":
    app()
