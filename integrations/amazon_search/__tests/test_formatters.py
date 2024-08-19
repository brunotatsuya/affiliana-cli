# Fixtures from conftest.py
from typing import List
import pytest
from app.interfaces.dtos.amazon_product_snapshot import AmazonProductSnapshot
from integrations.amazon_search.formatters import format_search


@pytest.fixture(scope="module")
def products(amazon_search: dict):
    return format_search(amazon_search)


def test_should_extract_only_products_that_have_asin_when_html_is_a_search_result_page(
    products: List[AmazonProductSnapshot],
):
    assert all(p.asin for p in products)


def test_should_correctly_extract_the_product_title_when_html_is_a_search_result_page(
    products: List[AmazonProductSnapshot],
):
    target_product = next(p for p in products if p.asin == "B073SZRRXJ")
    assert (
        target_product.title
        == "Petlinks HappyNip Crinkle Chameleon Cat Toy, Contains Silvervine & Catnip - Green, One Size"
    )


def test_should_correctly_extract_the_product_price_when_html_is_a_search_result_page(
    products: List[AmazonProductSnapshot],
):
    target_product = next(p for p in products if p.asin == "B073SZRRXJ")
    assert target_product.price_usd == 4.99


def test_should_correctly_extract_the_product_rating_when_html_is_a_search_result_page(
    products: List[AmazonProductSnapshot],
):
    target_product = next(p for p in products if p.asin == "B073SZRRXJ")
    assert target_product.rating == 4.4


def test_should_correctly_extract_the_product_reviews_when_html_is_a_search_result_page(
    products: List[AmazonProductSnapshot],
):
    target_product = next(p for p in products if p.asin == "B073SZRRXJ")
    assert target_product.reviews == 7124


def test_should_correctly_extract_the_product_last_month_buys_when_html_is_a_search_result_page(
    products: List[AmazonProductSnapshot],
):
    target_product = next(p for p in products if p.asin == "B073SZRRXJ")
    assert target_product.bought_last_month == 600


def test_should_mark_the_product_as_sponsored_when_it_is(products: List[AmazonProductSnapshot]):
    target_product = next(p for p in products if p.asin == "B0BJZKYL1D")
    assert target_product.is_sponsored


def test_should_not_mark_the_product_as_sponsored_when_it_is_not(products: List[AmazonProductSnapshot]):
    target_product = next(p for p in products if p.asin == "B0BGBHXSWH")
    assert not target_product.is_sponsored


def test_should_not_filter_out_products_that_have_no_reviews_data(products: List[AmazonProductSnapshot]):
    target_product = next(p for p in products if p.asin == "B0CMT4P1K8")
    assert target_product.reviews is None


def test_should_filter_out_products_that_have_no_pricing_data(products: List[AmazonProductSnapshot]):
    assert all(p.price_usd for p in products)


def test_should_remove_duplicated_products_and_keep_the_first_one(products: List[AmazonProductSnapshot]):
    target_product = next(p for p in products if p.asin == "B0C7GMX4FT")

    assert target_product.is_sponsored == True
    assert len(products) == len(set(p.asin for p in products))
