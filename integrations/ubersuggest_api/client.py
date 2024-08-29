from typing import List
import inject

from app.exceptions import (
    NoDataFromSourceException,
    DataFetchError,
    AuthenticationError,
)
from app.interfaces.dtos.keyword_report import KeywordReport
from config import Config
from integrations.constants import HttpMethodEnum, RetryStrategyEnum
from integrations.retriable_http_client import RetriableHttpClient
from .formatters import format_get_keyword_report
from .constants import DEFAULT_MARKET_LANGUAGE, DEFAULT_MARKET_LOCATION_ID


class UbersuggestAPIClient:
    """
    A client for interacting with the Ubersuggest API.
    """

    @inject.autoparams()
    def __init__(self, config: Config, http_client: RetriableHttpClient):
        self.config = config
        self.http_client = http_client
        self.base_uri = "https://app.neilpatel.com/api"
        self.authorization_token = None

        self.__update_authorization_token(use_proxy=False)

    def __update_authorization_token(self, use_proxy: bool) -> str:
        """
        Updates the authorization token within the class.

        Args:
            use_proxy (bool): Flag indicating whether to use a proxy for the request.

        Raises:
            Exception: If the request to get the authorization token fails.
        """
        uri = f"{self.base_uri}/get_token?debug=app_norecaptcha"

        if use_proxy:
            proxies = {
                "http": self.config.PROXY_PROVIDER_CREDENTIALS,
                "https": self.config.PROXY_PROVIDER_CREDENTIALS,
            }
            response = self.http_client.request(
                HttpMethodEnum.GET, uri, proxies=proxies
            )
        else:
            response = self.http_client.request(HttpMethodEnum.GET, uri)

        if response.status_code != 200:
            raise AuthenticationError(
                f"Failed to get authorization token: {response.text} - {response.status_code}"
            )

        self.authorization_token = response.json().get("token")

    def __get_request_headers(self) -> dict:
        """
        Returns general request headers with the most recent authorization token.

        Returns:
            dict: The request headers.
        """
        return {
            "accept": "application/json, text/plain, */*",
            "authorization": f"Bearer {self.authorization_token}",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        }

    def __before_retry(self) -> dict:
        """
        Updates the authorization token and returns the request headers.
        To be used as a before_retry function in the http client.

        Returns:
            dict: The request headers.
        """
        self.__update_authorization_token(use_proxy=True)
        return self.__get_request_headers()

    def __make_request(self, method: HttpMethodEnum, uri: str, **kwargs) -> dict:
        """
        Makes a request to the specified URI using the given HTTP method.
        Centralizes the logic for making requests to the Ubersuggest API.

        Args:
            method (HttpMethodEnum): The HTTP method to use for the request.
            uri (str): The URI to send the request to.
            **kwargs: Additional keyword arguments to pass to the http client.

        Returns:
            dict: The JSON response from the request.

        Raises:
            DataFetchError: If the request fails with a non-200 status code.
        """
        response = self.http_client.request(
            method,
            uri,
            retry_times=2,
            retry_strategy=RetryStrategyEnum.BEFORE_RETRY_FUNCTION,
            before_retry=self.__before_retry,
            headers=self.__get_request_headers(),
            **kwargs,
        )
        if response.status_code != 200:
            raise DataFetchError(
                f"Failed request to '{uri}': {response.text} - {response.status_code}"
            )

        return response.json()

    def get_keyword_info(
        self,
        keyword: str,
        language: str = DEFAULT_MARKET_LANGUAGE,
        loc_id: int = DEFAULT_MARKET_LOCATION_ID,
    ) -> dict:
        """
        Retrieves keyword information from the Ubersuggest API.

        Args:
            keyword (str): The keyword to retrieve information for.
            language (str): The language of the keyword.
            loc_id (int): The location ID for the keyword.

        Returns:
            UbersuggestKeywordInfo: An object containing the retrieved keyword information.

        Raises:
            DataFetchError: If the request to the Ubersuggest API fails.

        """
        uri = f"{self.base_uri}/keyword_info?keyword={keyword}&language={language}&locId={loc_id}"
        return self.__make_request(HttpMethodEnum.GET, uri)

    def get_serp_analysis(
        self,
        keyword: str,
        language: str = DEFAULT_MARKET_LANGUAGE,
        loc_id: int = DEFAULT_MARKET_LOCATION_ID,
    ) -> dict:
        """
        Retrieves SERP (Search Engine Results Page) analysis from the Ubersuggest API.

        Args:
            keyword (str): The keyword to retrieve SERP analysis for.
            language (str): The language of the keyword.
            loc_id (int): The location ID for the keyword.

        Returns:
            dict: A dictionary containing the retrieved SERP analysis.

        Raises:
            DataFetchError: If the request to the Ubersuggest API fails.

        """
        uri = f"{self.base_uri}/serp_analysis?keyword={keyword}&language={language}&locId={loc_id}"
        return self.__make_request(HttpMethodEnum.GET, uri)

    def get_matching_keywords(
        self,
        keyword: str,
        language: str = DEFAULT_MARKET_LANGUAGE,
        loc_id: int = DEFAULT_MARKET_LOCATION_ID,
    ) -> dict:
        """
        Fethes matching keywords based on the provided keyword.

        Args:
            keyword (str): The keyword to search for matching keywords.
            language (str, optional): The language for the market. Defaults to DEFAULT_MARKET_LANGUAGE.
            loc_id (int, optional): The location ID for the market. Defaults to DEFAULT_MARKET_LOCATION_ID.

        Returns:
            dict: A dictionary containing the matching keywords.

        Raises:
            DataFetchError: If the request to the Ubersuggest API fails.

        """
        uri = f"{self.base_uri}/match_keywords"
        body = {
            "language": language,
            "locId": loc_id,
            "filters": {},
            "sortby": "-searchVolume",
            "keywords": [keyword],
            "previousKey": 0,
            "limit": 10,
        }
        return self.__make_request(HttpMethodEnum.POST, uri, json=body)

    def get_domain_counts(self, urls: List[str]) -> dict:
        """
        Retrieves domain counts from the Ubersuggest API.

        Args:
            urls (list): A list of URLs to retrieve domain counts for.

        Returns:
            dict: A dictionary containing the retrieved domain counts.

        Raises:
            DataFetchError: If the request to the Ubersuggest API fails.

        """
        uri = f"{self.base_uri}/domain_counts"
        body = {
            "domains": urls,
        }
        return self.__make_request(HttpMethodEnum.POST, uri, json=body)

    def get_keyword_report(
        self,
        keyword: str,
        language: str = DEFAULT_MARKET_LANGUAGE,
        loc_id: int = DEFAULT_MARKET_LOCATION_ID,
    ) -> KeywordReport:
        """
        Retrieves a keyword report for the specified keyword.

        Args:
            keyword (str): The keyword to retrieve the report for.
            language (str, optional): The language for the market. Defaults to DEFAULT_MARKET_LANGUAGE.
            loc_id (int, optional): The location ID for the market. Defaults to DEFAULT_MARKET_LOCATION_ID.

        Returns:
            KeywordReport: The keyword report containing information about the keyword, matching keywords,
            SERP (Search Engine Results Page) analysis, and keyword suggestions.

        Raises:
            DataFetchError: If any request to the Ubersuggest API fails.
            NoDataFromSourceException: If no data is available for the specified keyword.
        """

        keyword_info = self.get_keyword_info(keyword, language, loc_id)
        if keyword_info.get("noData") == True:
            raise NoDataFromSourceException(f"No data available for keyword: {keyword}")

        matching_keywords = self.get_matching_keywords(keyword, language, loc_id)
        serp_analysis = self.get_serp_analysis(keyword, language, loc_id)
        
        # Extract the first 20 URLs from the SERP analysis to get domain counts
        urls = [entry["url"] for entry in serp_analysis["serpEntries"][:20]]
        domain_counts = self.get_domain_counts(urls)

        return format_get_keyword_report(
            keyword_info,
            matching_keywords,
            serp_analysis,
            domain_counts,
            language,
            loc_id,
        )
