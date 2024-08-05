from typing import List
import inject

from app.exceptions import DataFetchError
from integrations.google_suggest.formatters import format_get_suggestions
from .constants import DEFAULT_COUNTRY, DEFAULT_LANGUAGE
from ..constants import HttpMethodEnum
from ..retriable_http_client import RetriableHttpClient


class GoogleSuggestClient:
    """
    A client for retrieving Google search suggestions.
    """

    @inject.autoparams()
    def __init__(self, http_client: RetriableHttpClient):
        self.http_client = http_client
        self.base_uri = "https://suggestqueries.google.com"

    def get_suggestions(
        self,
        query: str,
        country: str = DEFAULT_COUNTRY,
        language: str = DEFAULT_LANGUAGE,
    ) -> List[str]:
        """
        Retrieves search suggestions from Google.

        Args:
            query (str): The search query.
            country (str): The country code.
            language (str): The language code.

        Returns:
            List[str]: A list of search suggestions.

        Raises:
            DataFetchError: If the request fails.
        """
        uri = f"{self.base_uri}/complete/search?client=chrome&q={query}&hl={language}&gl={country}"
        response = self.http_client.request(HttpMethodEnum.GET, uri, headers={})
        if response.status_code != 200:
            raise DataFetchError(
                f"Failed to get suggestions: {response.text} - {response.status_code}"
            )
        return format_get_suggestions(response.json())
