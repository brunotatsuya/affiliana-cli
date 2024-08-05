from typer import Typer

from .niche_research_commands import niche_research_typer


typer_app = Typer()
typer_app.add_typer(niche_research_typer, name="niche_research")
