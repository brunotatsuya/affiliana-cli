import pytest
from unittest.mock import MagicMock

from app.exceptions.data import DataFetchError
from integrations.google_suggest.client import GoogleSuggestClient


class TestGoogleSuggestClient:

    @pytest.fixture(scope="class")
    def google_suggest_client(self):
        return GoogleSuggestClient()

    def test_should_return_suggestions_if_request_succeeds(
        self, google_suggest_client: GoogleSuggestClient, search: dict
    ):
        google_suggest_client.http_client.request.return_value.status_code = 200
        google_suggest_client.http_client.request.return_value.json = MagicMock(
            return_value=search
        )

        get_suggestions_response = google_suggest_client.get_suggestions("cat toys")

        assert get_suggestions_response == search[1]

    def test_should_raise_exception_if_request_fails(
        self, google_suggest_client: GoogleSuggestClient
    ):
        google_suggest_client.http_client.request.return_value.status_code = 500

        with pytest.raises(DataFetchError):
            google_suggest_client.get_suggestions("cat toys")
