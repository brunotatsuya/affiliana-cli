import inject
from typing import Annotated
from typer import Argument, Typer

from app.domain import ProductResearch

product_research_typer = Typer()


@product_research_typer.command("fetch_amazon_products")
def fetch_amazon_products_command(
    niche: Annotated[str, Argument(help="The main niche to perform research on.")]
):
    """Perform product research for the given niche."""
    fetch_amazon_products(niche)

@product_research_typer.command("fetch_amazon_products_for_candidates")
def fetch_amazon_products_for_candidates_command():
    """Perform product research for all niche candidates."""
    fetch_amazon_products_for_candidates()

@inject.params(product_research=ProductResearch)
def fetch_amazon_products(niche: str, product_research: ProductResearch):
    product_research.fetch_amazon_products_for_niche(niche)

@inject.params(product_research=ProductResearch)
def fetch_amazon_products_for_candidates(product_research: ProductResearch):
    product_research.fetch_amazon_products_for_candidates()