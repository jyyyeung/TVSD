import os
import sys
from typing import Optional

import typer
from dynaconf import settings

app = typer.Typer()


def setup_django_environment():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.tvsd_web.settings")
    try:
        import django

        django.setup()
    except ImportError:
        typer.echo("Django not installed. Please install with: pip install tvsd[web]")
        raise typer.Exit(1)


@app.command()
def runserver(
    port: Optional[int] = typer.Option(
        8000, "--port", "-p", help="Port to run server on"
    ),
    host: Optional[str] = typer.Option(
        "127.0.0.1", "--host", "-h", help="Host to run server on"
    ),
):
    """Run the TVSD web interface"""
    setup_django_environment()
    from django.core.management import execute_from_command_line

    execute_from_command_line([sys.argv[0], "runserver", f"{host}:{port}"])


def main():
    app()


if __name__ == "__main__":
    main()
