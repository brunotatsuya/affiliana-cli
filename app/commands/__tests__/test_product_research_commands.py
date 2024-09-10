import inject
import pytest

from app.commands.product_research_commands import fetch_amazon_products
from app.domain import ProductResearch


class TestProductResearchCommands:

    @pytest.fixture
    def product_research(self):
        return inject.instance(ProductResearch)

    def test_should_fetch_amazon_products_when_providing_niche(
        self, product_research: ProductResearch
    ):
        fetch_amazon_products("cat toys")
        product_research.fetch_amazon_products_for_niche.assert_called_with("cat toys")
