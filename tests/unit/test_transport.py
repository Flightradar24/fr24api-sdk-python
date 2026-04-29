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
    DEFAULT_TIMEOUT,
    DEFAULT_USER_AGENT,
    DEFAULT_POOL_LIMITS,
    DEFAULT_RETRIES,
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
    assert trans.timeout == DEFAULT_TIMEOUT
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
    assert headers["User-Agent"] == DEFAULT_USER_AGENT
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
    assert sent_headers["user-agent"] == DEFAULT_USER_AGENT
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


# --- Connection pool limits tests ---


def test_default_pool_limits_applied():
    """When no http_client or limits are given, SDK defaults are applied."""
    trans = HttpTransport(api_token=TEST_TOKEN)
    pool = trans._client._transport._pool
    assert pool._max_connections == DEFAULT_POOL_LIMITS.max_connections
    assert pool._max_keepalive_connections == DEFAULT_POOL_LIMITS.max_keepalive_connections
    assert pool._keepalive_expiry == DEFAULT_POOL_LIMITS.keepalive_expiry
    trans.close()


def test_custom_limits_applied():
    """User-supplied limits override the defaults."""
    custom_limits = httpx.Limits(
        max_connections=3, max_keepalive_connections=1, keepalive_expiry=2
    )
    trans = HttpTransport(api_token=TEST_TOKEN, limits=custom_limits)
    pool = trans._client._transport._pool
    assert pool._max_connections == 3
    assert pool._max_keepalive_connections == 1
    assert pool._keepalive_expiry == 2
    trans.close()


def test_user_provided_http_client_ignores_limits():
    """When http_client is provided, limits param is irrelevant."""
    user_client = httpx.Client(
        base_url="http://example.com",
        limits=httpx.Limits(max_connections=42),
    )
    custom_limits = httpx.Limits(max_connections=1)
    trans = HttpTransport(
        api_token=TEST_TOKEN, http_client=user_client, limits=custom_limits
    )
    # The user's client should be used as-is
    assert trans._client is user_client
    assert trans._client._transport._pool._max_connections == 42
    trans.close()


# --- reset() tests ---


@respx_mock
def test_reset_creates_new_working_client():
    """reset() closes the old client and creates a functional replacement."""
    trans = HttpTransport(api_token=TEST_TOKEN)
    old_client = trans._client

    trans.reset()

    assert old_client.is_closed
    assert not trans._client.is_closed
    assert trans._client is not old_client

    # New client should be functional
    route = respx_mock.get(FULL_TEST_URL).respond(200, json={"ok": True})
    response = trans.request("GET", TEST_API_ENDPOINT_PATH)
    assert response.status_code == 200
    assert route.called
    trans.close()


def test_reset_preserves_pool_limits():
    """reset() re-applies the same pool limits to the new client."""
    custom_limits = httpx.Limits(
        max_connections=7, max_keepalive_connections=2, keepalive_expiry=3
    )
    trans = HttpTransport(api_token=TEST_TOKEN, limits=custom_limits)
    trans.reset()
    pool = trans._client._transport._pool
    assert pool._max_connections == 7
    assert pool._max_keepalive_connections == 2
    assert pool._keepalive_expiry == 3
    trans.close()


def test_reset_raises_for_user_provided_client():
    """reset() raises RuntimeError when the transport uses an external client."""
    user_client = httpx.Client(base_url="http://example.com")
    trans = HttpTransport(api_token=TEST_TOKEN, http_client=user_client)
    with pytest.raises(RuntimeError, match="user-supplied http_client"):
        trans.reset()
    # Original client should still be usable
    assert not user_client.is_closed
    trans.close()


# --- Connection hardening tests ---


def test_default_retries_configured():
    """SDK-created clients use connection-establishment retries."""
    trans = HttpTransport(api_token=TEST_TOKEN)
    # retries are set on the HTTPTransport, which is _client._transport
    http_transport = trans._client._transport
    assert isinstance(http_transport, httpx.HTTPTransport)
    assert http_transport._pool._retries == DEFAULT_RETRIES
    trans.close()


def test_custom_retries():
    """User can override the retry count."""
    trans = HttpTransport(api_token=TEST_TOKEN, retries=5)
    assert trans._client._transport._pool._retries == 5
    trans.close()


def test_socket_options_include_keepalive():
    """SDK-created clients enable SO_KEEPALIVE on sockets."""
    import socket as _socket

    trans = HttpTransport(api_token=TEST_TOKEN)
    pool = trans._client._transport._pool
    sock_opts = pool._socket_options
    # SO_KEEPALIVE must always be present
    assert (_socket.SOL_SOCKET, _socket.SO_KEEPALIVE, 1) in sock_opts
    # TCP keepalive tuning constants should be present when the platform supports them
    if hasattr(_socket, "TCP_KEEPIDLE"):
        assert (_socket.IPPROTO_TCP, _socket.TCP_KEEPIDLE, 60) in sock_opts
    if hasattr(_socket, "TCP_KEEPINTVL"):
        assert (_socket.IPPROTO_TCP, _socket.TCP_KEEPINTVL, 10) in sock_opts
    if hasattr(_socket, "TCP_KEEPCNT"):
        assert (_socket.IPPROTO_TCP, _socket.TCP_KEEPCNT, 3) in sock_opts
    trans.close()


def test_granular_timeout_default():
    """Default timeout uses granular connect/read/write/pool values."""
    trans = HttpTransport(api_token=TEST_TOKEN)
    client_timeout = trans._client.timeout
    assert client_timeout.connect == 5
    assert client_timeout.read == 30
    assert client_timeout.write == 10
    assert client_timeout.pool == 5
    trans.close()


def test_float_timeout_backwards_compat():
    """Passing a plain float still works (applied to all timeout fields)."""
    trans = HttpTransport(api_token=TEST_TOKEN, timeout=15.0)
    client_timeout = trans._client.timeout
    assert client_timeout.connect == 15.0
    assert client_timeout.read == 15.0
    trans.close()


def test_httpx_timeout_object_passthrough():
    """Passing an httpx.Timeout object is used as-is."""
    custom = httpx.Timeout(connect=3, read=60, write=5, pool=2)
    trans = HttpTransport(api_token=TEST_TOKEN, timeout=custom)
    client_timeout = trans._client.timeout
    assert client_timeout.connect == 3
    assert client_timeout.read == 60
    assert client_timeout.pool == 2
    trans.close()


def test_reset_preserves_retries_and_socket_options():
    """reset() recreates the client with the same retries and socket opts."""
    import socket as _socket

    trans = HttpTransport(api_token=TEST_TOKEN, retries=4)
    trans.reset()
    assert trans._client._transport._pool._retries == 4
    sock_opts = trans._client._transport._pool._socket_options
    assert (_socket.SOL_SOCKET, _socket.SO_KEEPALIVE, 1) in sock_opts
    trans.close()
