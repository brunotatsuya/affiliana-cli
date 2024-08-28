from unittest.mock import patch
import pytest


from app.exceptions import DataFetchError
from integrations.amazon_search.client import AmazonSearchClient


class TestAmazonSearchClient:

    @pytest.fixture(scope="class")
    def amazon_search_client(self):
        return AmazonSearchClient()

    def test_should_return_html_if_request_succeeds(
        self, amazon_search_client: AmazonSearchClient, amazon_search: str
    ):
        amazon_search_client.http_client.request.return_value.status_code = 200
        amazon_search_client.http_client.request.return_value.text = amazon_search

        search_response = amazon_search_client.search("cat toys")

        assert search_response == amazon_search

    def test_should_raise_exception_if_request_fails(
        self, amazon_search_client: AmazonSearchClient
    ):
        amazon_search_client.http_client.request.return_value.status_code = 500

        with pytest.raises(DataFetchError):
            amazon_search_client.search("cat toys")

    def test_should_extract_and_format_products_from_html_when_get_products_for_keyword(
        self, amazon_search_client: AmazonSearchClient, amazon_search: str
    ):
        amazon_search_client.http_client.request.return_value.status_code = 200
        amazon_search_client.http_client.request.return_value.text = amazon_search

        with patch("integrations.amazon_search.client.format_search") as format_search:
            amazon_search_client.get_products_for_keyword("cat toys")
            format_search.assert_called_once_with(amazon_search)
