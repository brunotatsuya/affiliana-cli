import pytest
from app.exceptions import DataFormatError
from integrations.openai_api.formatters import (
    format_get_amazon_commission_rate_for_niches,
)


def test_should_produce_a_list_of_same_size_as_input():
    formatted = format_get_amazon_commission_rate_for_niches(
        "0A,1B", ["niche1", "niche2"]
    )
    assert len(formatted) == 2


def test_should_point_to_the_correct_niche_using_the_index():
    formatted = format_get_amazon_commission_rate_for_niches(
        "0A,1B", ["niche1", "niche2"]
    )
    assert formatted[0].niche == "niche1"
    assert formatted[1].niche == "niche2"


def test_should_point_to_the_correct_category_using_the_letter():
    formatted = format_get_amazon_commission_rate_for_niches(
        "0A,1B", ["niche1", "niche2"]
    )
    assert formatted[0].category == "Physical Books, Kitchen, Automotive"
    assert (
        formatted[1].category
        == "Apparel, Jewelry, Luggage, Shoes, Watches, Ring Devices, Handbags, Accessories"
    )


def test_should_point_to_the_correct_commission_rate_using_the_letter():
    formatted = format_get_amazon_commission_rate_for_niches(
        "0A,1B", ["niche1", "niche2"]
    )
    assert formatted[0].commission_rate == 4.5
    assert formatted[1].commission_rate == 4


def test_should_raise_data_format_error_when_formatting_fails():
    with pytest.raises(DataFormatError):
        format_get_amazon_commission_rate_for_niches(
            "not a good, response, from OpenAi", ["niche1", "niche2"]
        )
