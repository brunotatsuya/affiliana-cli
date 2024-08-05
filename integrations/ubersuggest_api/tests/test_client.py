import inject
import pytest
from unittest.mock import MagicMock

from integrations.retriable_http_client import RetriableHttpClient
from integrations.ubersuggest_api.client import UbersuggestAPIClient


@pytest.fixture(scope="module")
def ubersuggest_api_client():
    return UbersuggestAPIClient()


class TestUbersuggestAPIClientSuccessfulRequests:

    @pytest.fixture(autouse=True)
    def setup(self):
        http_client = inject.instance(RetriableHttpClient)
        http_client.request = MagicMock(return_value=MagicMock(status_code=200))

    def test_should_update_authorization_token_on_init(self):
        http_client = inject.instance(RetriableHttpClient)
        http_client.request.return_value.json = MagicMock(return_value={"token": "abc"})

        ubersuggest_api_client = UbersuggestAPIClient()

        assert ubersuggest_api_client.authorization_token == "abc"

    # keyword_info fixture coming from conftest.py
    def test_should_return_keyword_info_if_request_succeeds(
        self, ubersuggest_api_client: UbersuggestAPIClient, keyword_info: dict
    ):
        ubersuggest_api_client.http_client.request.return_value.json = MagicMock(
            return_value=keyword_info
        )

        get_keyword_info_response = ubersuggest_api_client.get_keyword_info("cat toys")

        assert get_keyword_info_response == keyword_info

    # matching_keywords fixture coming from conftest.py
    def test_should_return_matching_keywords_if_request_succeeds(
        self, ubersuggest_api_client: UbersuggestAPIClient, matching_keywords: dict
    ):
        ubersuggest_api_client.http_client.request.return_value.json = MagicMock(
            return_value=matching_keywords
        )

        get_matching_keywords_response = ubersuggest_api_client.get_matching_keywords(
            "cat toys"
        )

        assert get_matching_keywords_response == matching_keywords

    # serp_analysis fixture coming from conftest.py
    def test_should_return_serp_analysis_if_request_succeeds(
        self, ubersuggest_api_client: UbersuggestAPIClient, serp_analysis: dict
    ):
        ubersuggest_api_client.http_client.request.return_value.json = MagicMock(
            return_value=serp_analysis
        )

        get_serp_analysis_response = ubersuggest_api_client.get_serp_analysis(
            "cat toys"
        )

        assert get_serp_analysis_response == serp_analysis

    # suggestions_report fixture coming from conftest.py
    def test_should_return_suggestions_report_if_request_succeeds(
        self, ubersuggest_api_client: UbersuggestAPIClient, suggestions_report: dict
    ):
        ubersuggest_api_client.http_client.request.return_value.json = MagicMock(
            return_value=suggestions_report
        )

        get_suggestions_report_response = (
            ubersuggest_api_client.get_keyword_suggestions_report("cat toys")
        )

        assert get_suggestions_report_response == suggestions_report


class TestUbersuggestAPIClientFailingRequests:

    @pytest.fixture(autouse=True)
    def setup(self):
        http_client = inject.instance(RetriableHttpClient)
        http_client.request = MagicMock(return_value=MagicMock(status_code=500))

    def test_should_raise_exception_if_login_fails(self):
        with pytest.raises(Exception):
            UbersuggestAPIClient()

    def test_should_raise_exception_if_get_keyword_info_request_fails(
        self, ubersuggest_api_client: UbersuggestAPIClient
    ):
        with pytest.raises(Exception):
            ubersuggest_api_client.get_keyword_info("cat toys")

    def test_should_raise_exception_if_get_matching_keywords_request_fails(
        self, ubersuggest_api_client: UbersuggestAPIClient
    ):
        with pytest.raises(Exception):
            ubersuggest_api_client.get_matching_keywords("cat toys")

    def test_should_raise_exception_if_get_serp_analysis_request_fails(
        self, ubersuggest_api_client: UbersuggestAPIClient
    ):
        with pytest.raises(Exception):
            ubersuggest_api_client.get_serp_analysis("cat toys")

    def test_should_raise_exception_if_get_suggestions_report_request_fails(
        self, ubersuggest_api_client: UbersuggestAPIClient
    ):
        with pytest.raises(Exception):
            ubersuggest_api_client.get_keyword_suggestions_report("cat toys")
