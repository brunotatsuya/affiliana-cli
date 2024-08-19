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


@inject.params(product_research=ProductResearch)
def fetch_amazon_products(niche: str, product_research: ProductResearch):
    product_research.fetch_amazon_products_for_niche(niche)
