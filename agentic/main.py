import typer

from agentic.config import SETTINGS

app = typer.Typer()


@app.command()
def main() -> None:
    print("Welcome to Agentic!")
    print(f"OpenAI API Key: {SETTINGS.openai_api_key}")


if __name__ == "__main__":
    app()
