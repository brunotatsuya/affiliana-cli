import inject
from typer import Typer

from app.domain import Ideation

ideation_typer = Typer()


@ideation_typer.command("start_gsa_data_collector")
def start_gsa_data_collector():
    """Start data collector for the GPT-SEO-AMAZON (GSA) strategy."""
    start_gsa_data_collector()

@ideation_typer.command("generate_gsa_snapshot")
def generate_gsa_snapshot():
    """Generate a snapshot using the data collected for the GSA strategy."""
    generate_gsa_snapshot()

@inject.autoparams()
def start_gsa_data_collector(ideation: Ideation):
    ideation.start_gsa_data_collector()

@inject.autoparams()
def generate_gsa_snapshot(ideation: Ideation):
    ideation.generate_gsa_snapshot()