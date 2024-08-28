import inject
import pytest
from unittest.mock import MagicMock

from app.exceptions import AuthenticationError, DataFetchError
from integrations.constants import HttpMethodEnum
from integrations.retriable_http_client import RetriableHttpClient
from integrations.ubersuggest_api.client import UbersuggestAPIClient


class TestUbersuggestAPIClientSuccessfulRequests:

    @pytest.fixture(scope="class")
    def ubersuggest_api_client(self):
        http_client = inject.instance(RetriableHttpClient)
        http_client.request = MagicMock(return_value=MagicMock(status_code=200))
        return UbersuggestAPIClient()

    def test_should_update_authorization_token_on_init(self):
        http_client = MagicMock()
        http_client.request.return_value.status_code = 200
        http_client.request.return_value.json = MagicMock(return_value={"token": "abc"})

        ubersuggest_api_client = UbersuggestAPIClient(http_client=http_client)

        assert ubersuggest_api_client.authorization_token == "abc"

    def test_should_use_proxy_when_getting_authorization_token_if_flagged(
        self, ubersuggest_api_client: UbersuggestAPIClient
    ):
        ubersuggest_api_client._UbersuggestAPIClient__update_authorization_token(
            use_proxy=True
        )

        ubersuggest_api_client.http_client.request.assert_called_with(
            HttpMethodEnum.GET,
            f"{ubersuggest_api_client.base_uri}/get_token?debug=app_norecaptcha",
            proxies={
                "http": ubersuggest_api_client.config.PROXY_PROVIDER_CREDENTIALS,
                "https": ubersuggest_api_client.config.PROXY_PROVIDER_CREDENTIALS,
            },
        )

    def test_should_not_use_proxy_when_getting_authorization_token_if_not_flagged(
        self, ubersuggest_api_client: UbersuggestAPIClient
    ):
        ubersuggest_api_client._UbersuggestAPIClient__update_authorization_token(
            use_proxy=False
        )

        ubersuggest_api_client.http_client.request.assert_called_with(
            HttpMethodEnum.GET,
            f"{ubersuggest_api_client.base_uri}/get_token?debug=app_norecaptcha",
        )

    def test_should_return_request_headers_with_correct_authorization_token(
        self, ubersuggest_api_client: UbersuggestAPIClient
    ):
        ubersuggest_api_client.authorization_token = "def"
        headers = ubersuggest_api_client._UbersuggestAPIClient__get_request_headers()

        assert headers == {
            "accept": "application/json, text/plain, */*",
            "authorization": "Bearer def",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        }

    def test_should_update_authorization_token_using_proxy_on_before_retry(
        self, ubersuggest_api_client: UbersuggestAPIClient
    ):
        ubersuggest_api_client._UbersuggestAPIClient__update_authorization_token = (
            MagicMock()
        )
        ubersuggest_api_client._UbersuggestAPIClient__before_retry()
        ubersuggest_api_client._UbersuggestAPIClient__update_authorization_token.assert_called_with(
            use_proxy=True
        )

    def test_should_return_request_headers_on_before_retry(
        self, ubersuggest_api_client: UbersuggestAPIClient
    ):
        ubersuggest_api_client._UbersuggestAPIClient__get_request_headers = MagicMock()
        ubersuggest_api_client._UbersuggestAPIClient__before_retry()
        ubersuggest_api_client._UbersuggestAPIClient__get_request_headers.assert_called_once()

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

    def test_should_return_domain_counts_if_request_suceeds(
        self, ubersuggest_api_client: UbersuggestAPIClient, domain_counts: dict
    ):
        ubersuggest_api_client.http_client.request.return_value.json = MagicMock(
            return_value=domain_counts
        )

        get_domain_counts_response = ubersuggest_api_client.get_domain_counts(
            [
                "http://www.chewy.com/b/toys-326",
                "http://www.meowingtons.com/collections/cat-toys",
            ]
        )

        assert get_domain_counts_response == domain_counts


class TestUbersuggestAPIClientFailingRequests:

    @pytest.fixture(scope="class")
    def ubersuggest_api_client(self):
        http_client = inject.instance(RetriableHttpClient)
        http_client.request.return_value.status_code = 200
        client = UbersuggestAPIClient()
        client.http_client.request.return_value.status_code = 500
        return client

    def test_should_raise_exception_if_fails_to_get_valid_authentication_token(
        self, ubersuggest_api_client: UbersuggestAPIClient
    ):
        with pytest.raises(AuthenticationError):
            ubersuggest_api_client._UbersuggestAPIClient__update_authorization_token(
                use_proxy=False
            )

    def test_should_raise_exception_if_get_keyword_info_request_fails(
        self, ubersuggest_api_client: UbersuggestAPIClient
    ):
        with pytest.raises(DataFetchError):
            ubersuggest_api_client.get_keyword_info("cat toys")

    def test_should_raise_exception_if_get_matching_keywords_request_fails(
        self, ubersuggest_api_client: UbersuggestAPIClient
    ):
        with pytest.raises(DataFetchError):
            ubersuggest_api_client.get_matching_keywords("cat toys")

    def test_should_raise_exception_if_get_serp_analysis_request_fails(
        self, ubersuggest_api_client: UbersuggestAPIClient
    ):
        with pytest.raises(DataFetchError):
            ubersuggest_api_client.get_serp_analysis("cat toys")

    def test_should_raise_exception_if_get_domain_counts_request_fails(
        self, ubersuggest_api_client: UbersuggestAPIClient
    ):
        with pytest.raises(DataFetchError):
            ubersuggest_api_client.get_domain_counts(
                [
                    "http://www.chewy.com/b/toys-326",
                    "http://www.meowingtons.com/collections/cat-toys",
                ]
            )
