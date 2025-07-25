import typer

from evals.datasets import datasets_app
from evals.experiments import experiments_app

app = typer.Typer()

app.add_typer(datasets_app, name="datasets", help="Execute dataset commands")
app.add_typer(experiments_app, name="experiments", help="Execute experiment commands")

if __name__ == "__main__":
    app()
