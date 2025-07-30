# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Custom exceptions for the Flightradar24 SDK."""

from typing import Optional, Union, Any

import httpx


class Fr24SdkError(Exception):
    """Base class for all Flightradar24 SDK errors."""

    pass


class TransportError(Fr24SdkError):
    """Indicates an error during HTTP transport (e.g., network issue, timeout)."""

    def __init__(self, message: str, *, request: Optional[httpx.Request] = None):
        super().__init__(message)
        self.request = request


class ApiError(Fr24SdkError):
    """Base class for errors returned by the Flightradar24 API (4xx/5xx responses)."""

    def __init__(
        self,
        message: str,
        *,
        request: httpx.Request,
        response: httpx.Response,
        body: Optional[Union[str, dict[str, Any]]] = None,
    ):
        super().__init__(message)
        self.request = request
        self.response = response
        self.status_code = response.status_code
        self.body = body  # Parsed JSON body if available, otherwise raw text
        self.headers = response.headers

    @property
    def status(self) -> int:
        """Alias for status_code for convenience."""
        return self.status_code

    @property
    def message(self) -> str:
        """Get the error message."""
        return str(self.args[0]) if self.args else ""

    @property
    def request_url(self) -> str:
        """Get the request URL as a string."""
        return str(self.request.url)

    def __str__(self) -> str:
        base_message = super().__str__()
        return f"{self.status_code} {self.response.reason_phrase}: {base_message} (URL: {self.request.url})"


class AuthenticationError(ApiError):
    """Indicates an authentication failure (401 Unauthorized)."""

    pass


class RateLimitError(ApiError):
    """Indicates that the API rate limit has been exceeded (402 Payment Required or 429 Too Many Requests)."""

    pass


class PaymentRequiredError(RateLimitError):
    """Specifically for 402 Payment Required errors, often meaning credit limit reached."""

    pass


class BadRequestError(ApiError):
    """Indicates a client-side error, like invalid parameters (400 Bad Request)."""

    pass


class NotFoundError(ApiError):
    """Indicates that the requested resource was not found (404 Not Found)."""

    pass
