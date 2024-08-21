from typing import Optional
import inject
import requests
import time

from monitoring.logger import Logger, LogTypeEnum
from .constants import SUCCESSFUL_STATUS_CODES, HttpMethodEnum


class RetriableHttpClient:
    """
    A class for making HTTP requests with retries.
    """

    @inject.autoparams()
    def __init__(self, logger: Logger):
        self.logger = logger

    def get_session(self) -> requests.Session:
        """
        Returns a new instance of requests.Session.

        Returns:
            requests.Session: A new instance of requests.Session.
        """
        return requests.Session()

    def request(
        self,
        method: HttpMethodEnum,
        uri: str,
        headers: Optional[dict] = {},
        retry_times: Optional[int] = 0,
        cooldown: Optional[int] = 0,
        before_retry: Optional[callable] = None,
        session: Optional[requests.Session] = None,
        **kwargs,
    ):
        """
        Makes an HTTP request using the specified method and URI.

        Args:
            method (HttpMethodEnum): The HTTP method.
            uri (str): The URI to send the request to.
            headers (dict, optional): The headers to include in the request. Defaults is {}.
            retry_times (int, optional): The number of times to retry the request if it fails. Default is 0.
            cooldown (int, optional): The cooldown time in seconds between retries. Default is 0.
            before_retry (callable, optional): A function to execute before each retry. Can return new headers. Default is None.
            session (requests.Session, optional): The requests session to use. Default is None.
            **kwargs: Additional keyword arguments to pass to the requests library.

        Returns:
            requests.Response: The response object from the HTTP request.

        Raises:
            ValueError: If the provided HTTP method is not supported.
        """

        if method in HttpMethodEnum.__members__.values():
            self.logger.notify(
                f"Making {method.value.upper()} request to {uri}", LogTypeEnum.DEBUG
            )
            if session:
                response = session.request(method.value, uri, headers=headers, **kwargs)
            else:
                response = requests.request(
                    method.value, uri, headers=headers, **kwargs
                )
            if response.status_code not in SUCCESSFUL_STATUS_CODES and retry_times:
                time.sleep(cooldown)
                if before_retry:
                    new_headers = before_retry()
                    if new_headers:
                        headers = new_headers
                response = self.request(
                    method,
                    uri,
                    headers,
                    retry_times - 1,
                    cooldown,
                    before_retry,
                    session,
                    **kwargs,
                )
            return response
        raise ValueError(f'Method "{method.value}" is invalid.')
