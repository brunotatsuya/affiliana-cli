from typer import Typer

from .niche_research_commands import niche_research_typer
from .product_research_commands import product_research_typer
from .ideation_commands import ideation_typer

typer_app = Typer()
typer_app.add_typer(niche_research_typer, name="niche_research")
typer_app.add_typer(product_research_typer, name="product_research")
typer_app.add_typer(ideation_typer, name="ideation")