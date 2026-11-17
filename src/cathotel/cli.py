from pathlib import Path

import typer
from sqlmodel import Session

from cathotel.config import get_settings
from cathotel.database import create_database_engine, create_db_and_tables
from cathotel.services.capacity import CapacityImportError, import_capacity_csv

app = typer.Typer()
capacity_app = typer.Typer()
app.add_typer(capacity_app, name="capacity")


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


if __name__ == "__main__":
    app()
