import typer

app = typer.Typer()


@app.callback()
def main() -> None:
    pass


if __name__ == "__main__":
    app()
