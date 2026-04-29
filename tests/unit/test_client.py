# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Unit tests for the Client class."""

import pytest
import httpx

from fr24sdk.client import Client
from fr24sdk.transport import DEFAULT_POOL_LIMITS


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
