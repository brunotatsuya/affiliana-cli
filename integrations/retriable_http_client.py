from typing import Optional
import inject
import requests
import time

from config.config import Config
from monitoring.logger import Logger, LogTypeEnum
from .constants import SUCCESSFUL_STATUS_CODES, HttpMethodEnum, RetryStrategyEnum


class RetriableHttpClient:
    """
    A class for making HTTP requests with retries.
    """

    @inject.autoparams()
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger

    def get_session(self) -> requests.Session:
        """
        Returns a new instance of requests.Session.

        Returns:
            requests.Session: A new instance of requests.Session.
        """
        return requests.Session()

    def get_proxies(self) -> dict:
        """
        Returns a dictionary containing the proxy configuration.

        Returns:
            dict: A dictionary containing the proxy configuration.
        """
        return {
            "http": self.config.PROXY_PROVIDER_CREDENTIALS,
            "https": self.config.PROXY_PROVIDER_CREDENTIALS,
        }

    def request(
        self,
        method: HttpMethodEnum,
        uri: str,
        retry_times: Optional[int] = 0,
        cooldown: Optional[int] = 0,
        retry_strategy: Optional[RetryStrategyEnum] = None,
        before_retry: Optional[callable] = None,
        session: Optional[requests.Session] = None,
        **kwargs,
    ):
        """
        Makes an HTTP request using the specified method and URI.

        Args:
            method (HttpMethodEnum): The HTTP method.
            uri (str): The URI to send the request to.
            retry_times (int, optional): The number of times to retry the request if it fails. Default is 0.
            cooldown (int, optional): The cooldown time in seconds between retries. Default is 0.
            retry_strategy (RetryStrategyEnum, optional): The retry strategy to use. Default is None.
            before_retry (callable, optional): A function to execute before each retry. Can return new headers.
                                               Will execute only if retry_strategy is BEFORE_RETRY_FUNCTION. Default is None.
            session (requests.Session, optional): The requests session to use. Default is None.
            **kwargs: Additional keyword arguments to pass to the requests library.

        Returns:
            requests.Response: The response object from the HTTP request.

        Raises:
            ValueError: If the provided HTTP method is not supported.
        """

        if method not in HttpMethodEnum.__members__.values():
            raise ValueError(f'Method "{method.value}" is invalid.')

        self.logger.notify(
            f"Making {method.value.upper()} request to {uri}", LogTypeEnum.DEBUG
        )

        request_agent = session if session else requests
        response = request_agent.request(method.value, uri, **kwargs)

        while response.status_code not in SUCCESSFUL_STATUS_CODES and retry_times:
            retry_times -= 1
            time.sleep(cooldown)
            self.logger.notify(
                f"Retrying {method.value.upper()} request to {uri} ({retry_times} left)", LogTypeEnum.DEBUG
            )

            if retry_strategy == RetryStrategyEnum.BEFORE_RETRY_FUNCTION and before_retry:
                new_headers = before_retry()
                if new_headers:
                    kwargs["headers"] = new_headers

            elif retry_strategy == RetryStrategyEnum.USE_PROXY:
                proxies = self.get_proxies()
                kwargs["proxies"] = proxies

            response = request_agent.request(method.value, uri, **kwargs)
            
        return response
