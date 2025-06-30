# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Handles low-level HTTP communication with the Flightradar24 API."""

import os
import logging
from typing import Any, Optional, Union, Mapping, Sequence, Type

import httpx

from .exceptions import (
    ApiError,
    AuthenticationError,
    RateLimitError,
    TransportError,
    PaymentRequiredError,
    BadRequestError,
    NotFoundError,
)

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://fr24api.flightradar24.com"
DEFAULT_API_VERSION = "v1"
DEFAULT_TIMEOUT_SECONDS = 30


class HttpTransport:
    """Manages HTTP requests to the Flightradar24 API, including auth and error handling."""

    def __init__(
        self,
        api_token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        api_version: str = DEFAULT_API_VERSION,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        http_client: Optional[httpx.Client] = None,
    ):
        self.api_token = api_token or os.environ.get("FR24_API_TOKEN")
        if not self.api_token:
            logger.warning(
                "FR24_API_TOKEN not provided or found in environment. API calls will likely fail."
            )

        self.base_url = base_url
        self.api_version = api_version
        self.timeout = timeout

        self._client: httpx.Client = http_client or httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
        )

    def _get_default_headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Accept-Version": self.api_version,
        }
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers

    def request(
        self,
        method: str,
        path: str,
        params: Optional[
            Mapping[str, Union[str, int, float, Sequence[Union[str, int, float]]]]
        ] = None,
        json_data: Optional[Any] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> httpx.Response:
        """Makes an HTTP request to the API."""

        request_headers = self._get_default_headers()
        if headers:
            request_headers.update(headers)

        log_url = f"{str(self._client.base_url).rstrip('/')}/{path.lstrip('/')}"

        logger.debug(
            f"Request: {method} {log_url} Params: {params} JSON: {json_data} Headers: {request_headers}"
        )

        try:
            response = self._client.request(
                method=method,
                url=path,
                params=params,
                json=json_data,
                headers=request_headers,
            )
            logger.debug(
                f"Response: {response.status_code} {response.reason_phrase} "
                f"URL: {response.url} Headers: {response.headers}"
            )
            if logger.isEnabledFor(logging.DEBUG):
                try:
                    debug_body = response.json()
                except ValueError:
                    debug_body = response.text[:500] + (
                        "... (truncated)" if len(response.text) > 500 else ""
                    )
                logger.debug(f"Response body: {debug_body}")

            response.raise_for_status()
            return response

        except httpx.HTTPStatusError as e:
            self._handle_http_status_error(e)
            raise  # Should be unreachable due to _handle_http_status_error always raising
        except httpx.TimeoutException as e:  # Catch specific httpx errors
            logger.error(f"Request timed out: {method} {log_url}")
            raise TransportError(
                f"Request timed out: {method} {log_url}", request=e.request
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Request failed: {method} {log_url} - {e}")
            raise TransportError(
                f"Request failed: {method} {log_url} - {e}", request=e.request
            ) from e

    def _handle_http_status_error(self, exc: httpx.HTTPStatusError) -> None:
        """Maps HTTPStatusError to a more specific ApiError subclass and raises it."""
        response = exc.response
        request = exc.request
        status_code = response.status_code

        try:
            body_content: Union[dict[str, Any], str] = response.json()
            if isinstance(body_content, dict):
                error_message_detail = body_content.get(
                    "details", body_content.get("message", response.text)
                )
            else:
                error_message_detail = str(body_content)
        except ValueError:  # Not JSON
            body_content = response.text
            error_message_detail = response.text

        full_request_url = str(request.url)
        error_message = f"{request.method} {full_request_url} -> {status_code} {response.reason_phrase}: {error_message_detail}"

        logger.info(
            f"API Error {status_code} for {request.method} {full_request_url}. Details: {error_message_detail}"
        )
        if status_code >= 500:
            logger.error(
                f"API Error {status_code} for {request.method} {full_request_url}: {error_message}"
            )

        logger.debug(f"API Error response body: {response.text}")

        specific_error_map: dict[int, Type[ApiError]] = {
            400: BadRequestError,
            401: AuthenticationError,
            402: PaymentRequiredError,
            404: NotFoundError,
            429: RateLimitError,
        }

        error_class = specific_error_map.get(status_code, ApiError)
        raise error_class(
            error_message, request=request, response=response, body=body_content
        ) from exc

    def close(self) -> None:
        """Closes the underlying HTTP client."""
        if hasattr(self, "_client") and self._client and not self._client.is_closed:
            self._client.close()

    def __enter__(self) -> "HttpTransport":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
