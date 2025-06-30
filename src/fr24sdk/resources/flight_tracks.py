# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Resource class for flight track data."""

from ..transport import HttpTransport
from ..models.flight import FlightTracksResponse


class FlightTracksResource:
    """Provides access to flight track data."""

    BASE_PATH = "/api/flight-tracks"

    def __init__(self, transport: HttpTransport):
        self._transport = transport

    def get(self, flight_id: str) -> FlightTracksResponse:
        """Get positional tracks for a specific flight.

        Args:
            flight_id: Flightradar24 id of active flight in hexadecimal (e.g., "34242a02").

        Returns:
            A FlightTracksResponse object containing the flight tracks.
        """
        response = self._transport.request(
            "GET", self.BASE_PATH, params={"flight_id": flight_id}
        )
        return FlightTracksResponse(data=response.json())
