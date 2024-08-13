import pytest
from unittest.mock import Mock, call, patch
from integrations.constants import HttpMethodEnum
from integrations.retriable_http_client import RetriableHttpClient


class TestRetriableHttpClient:

    @pytest.fixture
    def retriable_http_client(self):
        return RetriableHttpClient()

    @pytest.fixture
    def mock_request(self):
        with patch("requests.request") as mock_request:
            yield mock_request

    @pytest.mark.parametrize(
        "method",
        [
            HttpMethodEnum.GET,
            HttpMethodEnum.POST,
            HttpMethodEnum.PUT,
            HttpMethodEnum.PATCH,
            HttpMethodEnum.DELETE,
        ],
    )
    def test_should_return_response_if_method_is_supported(
        self,
        method: str,
        mock_request: Mock,
        retriable_http_client: RetriableHttpClient,
    ):
        mock_request.return_value.status_code = 200
        response = retriable_http_client.request(method, "http://example.com")
        assert response.status_code == 200

    def test_should_raise_exception_if_method_is_not_supported(
        self,
        retriable_http_client: RetriableHttpClient,
    ):
        with pytest.raises(Exception):
            retriable_http_client.request("INVALID_METHOD", "http://example.com")

    def test_should_retry_request_if_status_code_is_not_successful_and_retry_count(
        self,
        mock_request: Mock,
        retriable_http_client: RetriableHttpClient,
    ):
        mock_request.return_value.status_code = 500
        response = retriable_http_client.request(
            HttpMethodEnum.GET, "http://example.com", retry_times=3
        )
        assert response.status_code == 500
        assert mock_request.call_count == 4

    def test_should_not_retry_request_if_status_code_is_successful(
        self,
        mock_request: Mock,
        retriable_http_client: RetriableHttpClient,
    ):
        mock_request.return_value.status_code = 200
        response = retriable_http_client.request(
            HttpMethodEnum.GET, "http://example.com", retry_times=3
        )
        assert response.status_code == 200
        assert mock_request.call_count == 1

    def test_should_sleep_for_cooldown_time_between_retries(
        self,
        mock_request: Mock,
        retriable_http_client: RetriableHttpClient,
    ):
        mock_request.return_value.status_code = 500
        with patch("time.sleep") as mock_sleep:
            retriable_http_client.request(
                HttpMethodEnum.GET, "http://example.com", retry_times=3, cooldown=5
            )
            assert mock_sleep.call_count == 3
            assert mock_sleep.call_args_list == [call(5), call(5), call(5)]

    def test_should_execute_before_retry_function_before_each_retry(
        self,
        mock_request: Mock,
        retriable_http_client: RetriableHttpClient,
    ):
        mock_request.return_value.status_code = 500
        before_retry = Mock()
        retriable_http_client.request(
            HttpMethodEnum.GET,
            "http://example.com",
            retry_times=3,
            before_retry=before_retry,
        )
        assert before_retry.call_count == 3

    def test_should_update_headers_if_before_retry_function_returns_new_headers(
        self,
        mock_request: Mock,
        retriable_http_client: RetriableHttpClient,
    ):
        mock_request.return_value.status_code = 500
        before_retry = Mock(return_value={"new_header": "value"})
        retriable_http_client.request(
            HttpMethodEnum.GET,
            "http://example.com",
            headers={"old_header": "value"},
            retry_times=1,
            before_retry=before_retry,
        )
        assert mock_request.call_args_list == [
            call(
                "GET",
                "http://example.com",
                headers={"old_header": "value"},
            ),
            call(
                "GET",
                "http://example.com",
                headers={"new_header": "value"},
            ),
        ]

    def test_should_use_session_if_provided(
        self,
        mock_request: Mock,
        retriable_http_client: RetriableHttpClient,
    ):
        session = Mock()
        retriable_http_client.request(
            HttpMethodEnum.GET, "http://example.com", session=session
        )
        assert session.request.call_count == 1
        assert mock_request.call_count == 0
