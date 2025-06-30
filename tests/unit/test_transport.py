# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Unit tests for the HttpTransport class."""

import pytest
import httpx
from typing import Generator, Type, Any

from respx import mock as respx_mock  # Import mock for decorator

from fr24sdk.transport import (
    HttpTransport,
    DEFAULT_BASE_URL,
    DEFAULT_API_VERSION,
    DEFAULT_TIMEOUT_SECONDS,
)
from fr24sdk.exceptions import (
    ApiError,
    AuthenticationError,
    RateLimitError,
    TransportError,
    PaymentRequiredError,
    BadRequestError,
    NotFoundError,
    Fr24SdkError,
)

TEST_TOKEN = "test_api_token_123"
TEST_API_ENDPOINT_PATH = "/api/test/endpoint"
FULL_TEST_URL = f"{DEFAULT_BASE_URL}{TEST_API_ENDPOINT_PATH}"


# Helper to check if the request URL is in the exception message
def request_url_in_exc_message(exc: Fr24SdkError, expected_url: str) -> bool:
    """Checks if the request URL is present and correct in an exception message or attribute."""
    # Check if the exception has a request attribute with a URL
    if (
        hasattr(exc, "request")
        and exc.request is not None
        and hasattr(exc.request, "url")
    ):
        if str(exc.request.url) == expected_url:
            return True
    # Fallback: Check the string representation of the exception
    return expected_url in str(exc)


@pytest.fixture
def transport() -> Generator[HttpTransport, None, None]:
    t = HttpTransport(api_token=TEST_TOKEN)
    yield t
    t.close()


@pytest.fixture
def transport_no_token() -> Generator[HttpTransport, None, None]:
    t = HttpTransport(api_token=None)
    yield t
    t.close()


@pytest.fixture
def transport_with_env_token(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[HttpTransport, None, None]:
    monkeypatch.setenv("FR24_API_TOKEN", TEST_TOKEN)
    t = HttpTransport()
    yield t
    t.close()
    monkeypatch.delenv("FR24_API_TOKEN")


def test_transport_initialization_defaults():
    trans = HttpTransport(api_token=TEST_TOKEN)
    assert trans.api_token == TEST_TOKEN
    assert trans.base_url == DEFAULT_BASE_URL
    assert trans.api_version == DEFAULT_API_VERSION
    assert trans.timeout == DEFAULT_TIMEOUT_SECONDS
    assert isinstance(trans._client, httpx.Client)
    trans.close()


def test_transport_initialization_custom_values():
    custom_base_url = "https://custom.api.com"
    custom_api_version = "v2"
    custom_timeout = 10.0

    trans = HttpTransport(
        api_token="custom_token",
        base_url=custom_base_url,
        api_version=custom_api_version,
        timeout=custom_timeout,
    )
    assert trans.api_token == "custom_token"
    assert trans.base_url == custom_base_url
    assert trans.api_version == custom_api_version
    assert trans.timeout == custom_timeout
    trans.close()


def test_transport_uses_provided_httpx_client():
    mock_client = httpx.Client(base_url="http://mock.client")
    trans = HttpTransport(api_token=TEST_TOKEN, http_client=mock_client)
    assert trans._client == mock_client
    trans.close()  # This will close the client we provided
    assert mock_client.is_closed


def test_api_token_from_env(transport_with_env_token: HttpTransport) -> None:
    assert transport_with_env_token.api_token == TEST_TOKEN


def test_api_token_direct_takes_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FR24_API_TOKEN", "env_token")
    trans = HttpTransport(api_token="direct_token")
    assert trans.api_token == "direct_token"
    trans.close()


def test_default_headers(transport: HttpTransport) -> None:
    headers = transport._get_default_headers()
    assert headers["Accept"] == "application/json"
    assert headers["Accept-Version"] == DEFAULT_API_VERSION
    assert headers["Authorization"] == f"Bearer {TEST_TOKEN}"


@respx_mock  # Use the respx.mock decorator
@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "DELETE"])
def test_successful_request(method: str) -> None:
    expected_response_json = {"success": True, "data": "test_data"}
    # Use respx.method directly instead of respx_router.method
    route = getattr(respx_mock, method.lower())(FULL_TEST_URL).respond(
        status_code=200, json=expected_response_json
    )

    # No `with respx_router:` needed as @respx.mock handles it
    client_for_test = httpx.Client(base_url=DEFAULT_BASE_URL)
    transport_instance = HttpTransport(
        api_token=TEST_TOKEN, http_client=client_for_test
    )
    with transport_instance:
        response = transport_instance.request(method, TEST_API_ENDPOINT_PATH)

    assert response.status_code == 200
    assert response.json() == expected_response_json
    assert route.called


@respx_mock  # Use the respx.mock decorator
def test_request_with_params_and_custom_headers() -> None:  # Removed respx_router fixture
    params: dict[str, str | int] = {"key1": "value1", "key2": 123}
    custom_headers = {"X-Custom-Header": "custom_value"}
    # Use respx.method directly
    route = respx_mock.get(FULL_TEST_URL, params=params).respond(
        status_code=200, json={}
    )

    client_for_test = httpx.Client(base_url=DEFAULT_BASE_URL)
    transport_instance = HttpTransport(
        api_token=TEST_TOKEN, http_client=client_for_test
    )
    with transport_instance:
        transport_instance.request(
            "GET", TEST_API_ENDPOINT_PATH, params=params, headers=custom_headers
        )

    assert route.called
    # Ensure custom headers were sent, default ones are also present
    sent_headers = route.calls.last.request.headers
    assert sent_headers["x-custom-header"] == "custom_value"
    assert sent_headers["accept"] == "application/json"
    assert sent_headers["authorization"] == f"Bearer {TEST_TOKEN}"


@respx_mock  # Use the respx.mock decorator
@pytest.mark.parametrize(
    "status_code,error_json,expected_exception,error_message",
    [
        (400, {"message": "Bad input"}, BadRequestError, "Bad input"),
        (401, {"message": "Unauthorized"}, AuthenticationError, "Unauthorized"),
        (
            402,
            {"message": "Payment Required"},
            PaymentRequiredError,
            "Payment Required",
        ),
        (403, {"message": "Forbidden"}, ApiError, "Forbidden"),
        (404, {"message": "Not Found"}, NotFoundError, "Not Found"),
        (
            429,
            {"message": "Rate limit exceeded"},
            RateLimitError,
            "Rate limit exceeded",
        ),
        (500, {"message": "Server error"}, ApiError, "Server error"),
        (503, {"message": "Service unavailable"}, ApiError, "Service unavailable"),
    ],
)
def test_api_error_mapping(
    status_code: int,
    error_json: dict[str, Any],
    expected_exception: Type[ApiError],
    error_message: str,
) -> None:
    route = respx_mock.get(FULL_TEST_URL).respond(
        status_code=status_code, json=error_json
    )

    client_for_test = httpx.Client(base_url=DEFAULT_BASE_URL)
    transport_instance = HttpTransport(
        api_token=TEST_TOKEN, http_client=client_for_test
    )
    with pytest.raises(expected_exception) as exc_info:
        with transport_instance:
            transport_instance.request("GET", TEST_API_ENDPOINT_PATH)

    assert isinstance(exc_info.value, expected_exception)
    assert exc_info.value.status_code == status_code
    assert request_url_in_exc_message(exc_info.value, FULL_TEST_URL)
    if error_message:
        assert error_message in str(exc_info.value)

    assert route.called


@respx_mock  # Use the respx.mock decorator
def test_api_error_mapping_non_json_response() -> None:
    error_text = "An unexpected HTML error page"
    route = respx_mock.get(FULL_TEST_URL).respond(status_code=500, text=error_text)

    client_for_test = httpx.Client(base_url=DEFAULT_BASE_URL)
    transport_instance = HttpTransport(
        api_token=TEST_TOKEN, http_client=client_for_test
    )
    with pytest.raises(ApiError) as exc_info:
        with transport_instance:
            transport_instance.request("GET", TEST_API_ENDPOINT_PATH)

    assert exc_info.value.status_code == 500
    assert request_url_in_exc_message(exc_info.value, FULL_TEST_URL)
    assert error_text in str(exc_info.value)
    assert route.called


@respx_mock  # Use the respx.mock decorator
@pytest.mark.parametrize(
    "exception_to_raise,expected_sdk_exception,error_message_contains",
    [
        (
            httpx.TimeoutException(
                "Timeout!", request=httpx.Request("GET", FULL_TEST_URL)
            ),
            TransportError,
            "Request timed out",
        ),
        (
            httpx.ConnectError(
                "Cannot connect!", request=httpx.Request("GET", FULL_TEST_URL)
            ),
            TransportError,
            "Request failed",
        ),
        (
            httpx.NetworkError(
                "Network issue!", request=httpx.Request("GET", FULL_TEST_URL)
            ),
            TransportError,
            "Request failed",
        ),
    ],
)
def test_transport_level_errors(
    exception_to_raise: httpx.RequestError,
    expected_sdk_exception: Type[TransportError],
    error_message_contains: str,
) -> None:
    route = respx_mock.get(FULL_TEST_URL).mock(side_effect=exception_to_raise)

    client_for_test = httpx.Client(base_url=DEFAULT_BASE_URL)
    transport_instance = HttpTransport(
        api_token=TEST_TOKEN, http_client=client_for_test
    )
    with pytest.raises(expected_sdk_exception) as exc_info:
        with transport_instance:
            transport_instance.request("GET", TEST_API_ENDPOINT_PATH)

    assert isinstance(exc_info.value, expected_sdk_exception)
    assert error_message_contains in str(exc_info.value)
    if hasattr(exc_info.value, "request") and exc_info.value.request is not None:
        assert str(exc_info.value.request.url) == FULL_TEST_URL
    assert route.called


@respx_mock  # Use the respx.mock decorator
def test_transport_context_manager() -> None:  # respx_router fixture removed
    route = respx_mock.get(FULL_TEST_URL).respond(200)  # Use respx_mock

    raw_client_passed_to_transport = httpx.Client(base_url=DEFAULT_BASE_URL)

    # @respx.mock handles activation
    with HttpTransport(
        api_token=TEST_TOKEN, http_client=raw_client_passed_to_transport
    ) as transport_instance:
        transport_instance.request("GET", TEST_API_ENDPOINT_PATH)
        assert not raw_client_passed_to_transport.is_closed

    assert route.called
    assert raw_client_passed_to_transport.is_closed


@respx_mock  # Use the respx.mock decorator
def test_transport_explicit_close() -> None:  # respx_router fixture removed
    route = respx_mock.get(FULL_TEST_URL).respond(200)  # Use respx_mock

    raw_client_passed_to_transport = httpx.Client(base_url=DEFAULT_BASE_URL)
    transport_instance = HttpTransport(
        api_token=TEST_TOKEN, http_client=raw_client_passed_to_transport
    )

    # @respx.mock handles activation for the request call
    transport_instance.request("GET", TEST_API_ENDPOINT_PATH)

    assert not raw_client_passed_to_transport.is_closed
    transport_instance.close()

    assert route.called
    assert raw_client_passed_to_transport.is_closed
