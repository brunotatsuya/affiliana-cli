import json
import time
from functional import seq
from typing import List
import inject

from app.exceptions import NoDataFromSourceException, DataFetchError
from app.interfaces.dtos.keyword_report import KeywordReport, TypedKeyword
from config import Config
from integrations.constants import HttpMethodEnum
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
        self.login_session = None
        self.accounts_pool = list(
            zip(
                config.UBERSUGGEST_EMAILS.split(","),
                config.UBERSUGGEST_PASSWORDS.split(","),
            )
        )
        self.current_account_index = 0

        self.__rotate_credentials()

    def __get_request_headers(self):
        return {
            "Authorization ": f"Bearer {self.authorization_token}",
            "Accept": "application/json, text/plain, */*",
        }

    def __login(self, email: str, password: str):
        uri = f"{self.base_uri}/user/login?remember_me=false"
        body = {
            "email": email,
            "password": password,
        }

        self.login_session = self.http_client.get_session()

        payload = json.dumps(body)

        response = self.http_client.request(
            HttpMethodEnum.POST,
            uri,
            headers=self.__get_request_headers(),
            data=payload,
            session=self.login_session,
        )
        if response.status_code != 200:
            raise Exception(
                f"Failed to login: {response.text} - {response.status_code}"
            )

    def __update_authorization_token(self):
        uri = f"{self.base_uri}/get_token"

        response = self.http_client.request(
            HttpMethodEnum.GET, uri, headers={}, session=self.login_session
        )
        if response.status_code != 200:
            raise Exception(
                f"Failed to get authorization token: {response.text} - {response.status_code}"
            )

        self.authorization_token = response.json()["token"]

    def __rotate_credentials(self):
        email, password = self.accounts_pool[self.current_account_index]

        new_index = (self.current_account_index + 1) % len(self.accounts_pool)
        self.current_account_index = new_index

        self.__login(email, password)
        self.__update_authorization_token()
        return self.__get_request_headers()

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

        response = self.http_client.request(
            HttpMethodEnum.GET,
            uri,
            headers=self.__get_request_headers(),
            retry_times=len(self.accounts_pool),
            before_retry=self.__rotate_credentials,
        )
        if response.status_code != 200:
            raise DataFetchError(
                f"Failed to get keyword info: {response.text} - {response.status_code}"
            )

        return response.json()

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

        response = self.http_client.request(
            HttpMethodEnum.GET,
            uri,
            headers=self.__get_request_headers(),
            retry_times=len(self.accounts_pool),
            before_retry=self.__rotate_credentials,
        )
        if response.status_code != 200:
            raise DataFetchError(
                f"Failed to get SERP analysis: {response.text} - {response.status_code}"
            )

        return response.json()

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

        response = self.http_client.request(
            HttpMethodEnum.POST,
            uri,
            json=body,
            headers=self.__get_request_headers(),
            retry_times=len(self.accounts_pool),
            before_retry=self.__rotate_credentials,
        )
        if response.status_code != 200:
            raise DataFetchError(
                f"Failed to get matching keywords: {response.text} - {response.status_code}"
            )

        return response.json()

    def trigger_keyword_suggestions_report(
        self,
        keyword: str,
        base_suggestions: List[TypedKeyword],
        language: str = DEFAULT_MARKET_LANGUAGE,
        loc_id: int = DEFAULT_MARKET_LOCATION_ID,
    ):
        """
        Triggers a keyword suggestions report in the Ubersuggest API.

        Args:
            keyword (str): The keyword to trigger the report for.
            base_suggestions (List[TypedKeyword]): A list of base keywords to generate suggestions for.
            language (str): The language of the keyword.
            loc_id (int): The location ID for the keyword.

        Raises:
            DataFetchError: If the request to the Ubersuggest API fails.

        """
        uri = f"{self.base_uri}/keyword_suggestions_info"
        body = {
            "keyword": keyword,
            "language": language,
            "locId": loc_id,
            "keywords": {
                keyword: {
                    "SUGGESTION": seq(base_suggestions)
                    .map(lambda bs: bs.keyword)
                    .to_list()
                }
            },
        }

        response = self.http_client.request(
            HttpMethodEnum.POST,
            uri,
            json=body,
            headers=self.__get_request_headers(),
            retry_times=len(self.accounts_pool),
            before_retry=self.__rotate_credentials,
        )
        if response.status_code not in [200, 201, 202]:
            raise DataFetchError(
                f"Failed to trigger keyword suggestions report: {response.text} - {response.status_code}"
            )

    def get_keyword_suggestions_report(
        self,
        keyword: str,
        language: str = DEFAULT_MARKET_LANGUAGE,
        loc_id: int = DEFAULT_MARKET_LOCATION_ID,
    ) -> dict | None:
        """
        Retrieves a keyword suggestions report from the Ubersuggest API.

        Args:
            keyword (str): The keyword to retrieve the report for.
            language (str): The language of the keyword.
            loc_id (int): The location ID for the keyword.

        Returns:
            dict: A dictionary containing the retrieved keyword suggestions report.
            None: If the report took more than 60 seconds to generate.

        Raises:
            DataFetchError: If the request to the Ubersuggest API fails.

        """
        uri = f"{self.base_uri}/keyword_suggestions_info_task_status"
        body = {
            "language": language,
            "locId": loc_id,
            "filters": {},
            "sortby": "-searchVolume",
            "keywords": [keyword],
        }

        # Poll for the report up to 60 seconds
        poll_count = 0
        while True:
            response = self.http_client.request(
                HttpMethodEnum.POST,
                uri,
                json=body,
                headers=self.__get_request_headers(),
                retry_times=len(self.accounts_pool),
                before_retry=self.__rotate_credentials,
            )

            if response.status_code != 200:
                raise DataFetchError(
                    f"Failed to get keyword suggestions report: {response.text} - {response.status_code}"
                )

            response_data = response.json()

            if response_data.get("done") == True:
                return response_data

            if poll_count >= 2:
                return None

            time.sleep(30)
            poll_count += 1

    def get_keyword_report(
        self,
        keyword: str,
        suggestions: List[TypedKeyword],
        language: str = DEFAULT_MARKET_LANGUAGE,
        loc_id: int = DEFAULT_MARKET_LOCATION_ID,
    ) -> KeywordReport:
        """
        Retrieves a keyword report for the specified keyword.

        Args:
            keyword (str): The keyword to retrieve the report for.
            suggestions (List[TypedKeyword]): A list of suggestions for the keyword.
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

        self.trigger_keyword_suggestions_report(keyword, suggestions, language, loc_id)
        suggestions_report = self.get_keyword_suggestions_report(
            keyword, language, loc_id
        )

        return format_get_keyword_report(
            keyword_info,
            matching_keywords,
            serp_analysis,
            suggestions_report,
            language,
            loc_id,
        )
