import inject
from typer import Typer

from app.domain import Ideation

ideation_typer = Typer()


@ideation_typer.command("start_gsa_data_collector")
def start_gsa_data_collector():
    """Start data collector for the GPT-SEO-AMAZON (GSA) strategy."""
    start_gsa_data_collector()


@inject.autoparams()
def start_gsa_data_collector(ideation: Ideation):
    ideation.start_gsa_data_collector()
