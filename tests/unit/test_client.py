# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Unit tests for the Client class."""

import pytest
import httpx

from fr24sdk.client import Client
from fr24sdk.transport import DEFAULT_POOL_LIMITS, DEFAULT_RETRIES, DEFAULT_TIMEOUT


TEST_TOKEN = "test_api_token_123"


def test_client_default_limits_passthrough():
    """Client applies SDK default pool limits to its transport."""
    client = Client(api_token=TEST_TOKEN)
    pool = client.transport._client._transport._pool
    assert pool._max_connections == DEFAULT_POOL_LIMITS.max_connections
    assert pool._max_keepalive_connections == DEFAULT_POOL_LIMITS.max_keepalive_connections
    assert pool._keepalive_expiry == DEFAULT_POOL_LIMITS.keepalive_expiry
    client.close()


def test_client_custom_limits_passthrough():
    """Client forwards custom limits to the transport."""
    custom = httpx.Limits(max_connections=2, max_keepalive_connections=1, keepalive_expiry=1)
    client = Client(api_token=TEST_TOKEN, limits=custom)
    pool = client.transport._client._transport._pool
    assert pool._max_connections == 2
    assert pool._max_keepalive_connections == 1
    assert pool._keepalive_expiry == 1
    client.close()


def test_client_reset_recycles_pool():
    """Client.reset() replaces the underlying httpx.Client."""
    client = Client(api_token=TEST_TOKEN)
    old_http_client = client.transport._client

    client.reset()

    assert old_http_client.is_closed
    assert not client.transport._client.is_closed
    assert client.transport._client is not old_http_client
    client.close()


def test_client_reset_raises_for_user_provided_http_client():
    """Client.reset() raises when constructed with an external http_client."""
    user_client = httpx.Client(base_url="http://example.com")
    client = Client(api_token=TEST_TOKEN, http_client=user_client)
    with pytest.raises(RuntimeError, match="user-supplied http_client"):
        client.reset()
    assert not user_client.is_closed
    client.close()


def test_client_default_retries_passthrough():
    """Client applies default connection-establishment retries."""
    client = Client(api_token=TEST_TOKEN)
    assert client.transport._client._transport._pool._retries == DEFAULT_RETRIES
    client.close()


def test_client_custom_retries_passthrough():
    """Client forwards custom retries to the transport."""
    client = Client(api_token=TEST_TOKEN, retries=5)
    assert client.transport._client._transport._pool._retries == 5
    client.close()


def test_client_default_granular_timeout():
    """Client applies the SDK's granular timeout defaults."""
    client = Client(api_token=TEST_TOKEN)
    t = client.transport._client.timeout
    assert t == DEFAULT_TIMEOUT
    client.close()


def test_client_float_timeout_passthrough():
    """Client accepts a plain float timeout for backwards compat."""
    client = Client(api_token=TEST_TOKEN, timeout=42.0)
    t = client.transport._client.timeout
    assert t.connect == 42.0
    assert t.read == 42.0
    client.close()


def test_client_httpx_timeout_passthrough():
    """Client accepts an httpx.Timeout object."""
    custom = httpx.Timeout(connect=1, read=2, write=3, pool=4)
    client = Client(api_token=TEST_TOKEN, timeout=custom)
    t = client.transport._client.timeout
    assert t.connect == 1
    assert t.read == 2
    assert t.pool == 4
    client.close()
