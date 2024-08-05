from app.commands import typer_app
from config import setup_injector, setup_logger

setup_injector()
setup_logger()

# Entry point
typer_app()
