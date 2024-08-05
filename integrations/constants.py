from enum import Enum


class HttpMethodEnum(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


SUCCESSFUL_STATUS_CODES = [200, 201, 202, 204, 302]
