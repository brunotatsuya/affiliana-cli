from enum import Enum


class HttpMethodEnum(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

class RetryStrategyEnum(Enum):
    USE_PROXY = "USE_PROXY"
    BEFORE_RETRY_FUNCTION = "BEFORE_RETRY_FUNCTION"

SUCCESSFUL_STATUS_CODES = [200, 201, 202, 204, 302]
