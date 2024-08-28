import pytest
from unittest.mock import MagicMock, Mock, patch

from app.domain import ProductResearch


class TestProductResearch:
    @pytest.fixture
    def product_research(self):
        return ProductResearch(Mock(), Mock(), Mock(), Mock())

    def test_should_format_niche_name_when_fetching_new_niche(
        self, product_research: ProductResearch
    ):
        # Setup mocks
        product_research.amazon_search_client.get_products_for_keyword.return_value = []

        with patch(
            "app.domain.product_research.format_niche_name"
        ) as format_niche_name:
            product_research.fetch_amazon_products_for_niche("Test Niche")
            format_niche_name.assert_called_once_with("Test Niche")

    def test_should_fetch_products_using_niche_name(
        self, product_research: ProductResearch
    ):
        # Setup mocks
        product_research.amazon_search_client.get_products_for_keyword.return_value = []

        # Act
        product_research.fetch_amazon_products_for_niche("Test Niche")

        # Assert
        product_research.amazon_search_client.get_products_for_keyword.assert_called_once_with(
            "test niche"
        )

    def test_should_upsert_snapshot_for_each_product_from_search(
        self, product_research: ProductResearch
    ):
        # Setup mocks
        product_research.amazon_search_client.get_products_for_keyword.return_value = [
            {"asin": "ASIN1"},
            {"asin": "ASIN2"},
        ]
        product_research.niches_repository.find_or_insert_niche.return_value = (
            MagicMock()
        )
        product_research.niches_repository.find_or_insert_niche.return_value.id = 123

        # Act
        product_research.fetch_amazon_products_for_niche("Test Niche")

        # Assert
        product_research.amazon_products_repository.upsert_amazon_product.assert_any_call(
            {"asin": "ASIN1"}, 123
        )
        product_research.amazon_products_repository.upsert_amazon_product.assert_any_call(
            {"asin": "ASIN2"}, 123
        )
