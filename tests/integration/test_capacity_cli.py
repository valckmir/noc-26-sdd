from datetime import date

from sqlmodel import Session, select
from typer.testing import CliRunner

from cathotel import cli
from cathotel.config import Settings
from cathotel.database import create_database_engine
from cathotel.models import CapacityDate


runner = CliRunner()


def test_cli_import_persists_rows_and_invalid_upload_leaves_database_unchanged(
    tmp_path, monkeypatch
):
    database_path = tmp_path / "staff.sqlite"
    monkeypatch.setattr(
        cli,
        "get_settings",
        lambda: Settings(database_path=database_path, hotel_timezone="UTC"),
    )
    valid_csv = tmp_path / "valid.csv"
    valid_csv.write_text(
        "date,room_capacity\n2030-03-01,8\n2030-03-02,10\n",
        encoding="utf-8",
    )

    result = runner.invoke(cli.app, ["capacity", "import", str(valid_csv)])

    assert result.exit_code == 0, result.output
    assert "2" in result.output
    engine = create_database_engine(database_path)
    with Session(engine) as session:
        rows = session.exec(select(CapacityDate).order_by(CapacityDate.date)).all()
        before = [(row.date, row.room_capacity) for row in rows]
    assert before == [(date(2030, 3, 1), 8), (date(2030, 3, 2), 10)]

    invalid_csv = tmp_path / "invalid.csv"
    invalid_csv.write_text(
        "date,room_capacity\n2030-03-03,4\nnot-a-date,6\n",
        encoding="utf-8",
    )
    result = runner.invoke(cli.app, ["capacity", "import", str(invalid_csv)])

    assert result.exit_code != 0
    assert "row" in result.output.lower() or "date" in result.output.lower()
    with Session(engine) as session:
        rows = session.exec(select(CapacityDate).order_by(CapacityDate.date)).all()
    assert [(row.date, row.room_capacity) for row in rows] == before
