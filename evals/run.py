import typer

from evals.datasets import datasets_app

app = typer.Typer()

app.add_typer(datasets_app, name="datasets", help="Execute dataset commands")


if __name__ == "__main__":
    app()
