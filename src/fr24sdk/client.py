# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Main synchronous client for interacting with the Flightradar24 API."""

from typing import Optional, Any
import logging

import httpx

from .transport import HttpTransport
from .resources import (
    AirlinesResource,
    AirportsResource,
    FlightSummaryResource,
    FlightTracksResource,
    UsageResource,
    LiveResource,
    HistoricResource,
)

logger = logging.getLogger(__name__)


class Client:
    """Synchronous Flightradar24 API Client."""

    def __init__(
        self,
        api_token: Optional[str] = None,
        base_url: Optional[str] = None,
        api_version: Optional[str] = None,
        timeout: Optional[float] = None,
        http_client: Optional[httpx.Client] = None,
    ):
        """Initializes the Flightradar24 API Client.

        Args:
            api_token: Your Flightradar24 API token. If None, reads from FR24_API_TOKEN env var.
            base_url: The base URL for the API. Defaults to production API.
            api_version: The API version. Defaults to 'v1'.
            timeout: Request timeout in seconds. Defaults to 30s.
            http_client: An optional pre-configured httpx.Client instance.
        """
        transport_kwargs: dict[str, Any] = {}
        if api_token is not None:
            transport_kwargs["api_token"] = api_token
        if base_url is not None:
            transport_kwargs["base_url"] = base_url
        if api_version is not None:
            transport_kwargs["api_version"] = api_version
        if timeout is not None:
            transport_kwargs["timeout"] = timeout
        if http_client is not None:
            transport_kwargs["http_client"] = http_client

        self._transport = HttpTransport(**transport_kwargs)

        # Initialize resource namespaces
        self.airlines = AirlinesResource(self._transport)
        self.airports = AirportsResource(self._transport)
        self.flight_summary = FlightSummaryResource(self._transport)
        self.flight_tracks = FlightTracksResource(self._transport)
        self.usage = UsageResource(self._transport)
        self.live = LiveResource(self._transport)
        self.historic = HistoricResource(self._transport)

        logger.info("Flightradar24 Client initialized.")

    def close(self) -> None:
        """Closes the underlying HTTP transport client."""
        if self._transport:
            self._transport.close()
            logger.info("Flightradar24 Client transport closed.")

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    # Convenience property to access the underlying transport if needed for advanced use cases
    @property
    def transport(self) -> HttpTransport:
        return self._transport
