# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Resource class for interacting with airline-related API endpoints."""

from typing import Optional

from ..transport import HttpTransport
from ..models.airline import AirlineLight


class AirlinesResource:
    """Provides access to airline data."""

    def __init__(self, transport: HttpTransport):
        self._transport = transport

    def get_light(self, icao: str) -> Optional[AirlineLight]:
        """Get basic airline information by ICAO code.

        Args:
            icao: Airline ICAO code (e.g., "SAS", "DLH").

        Returns:
            An AirlineLight object if found. Raises NotFoundError if not found.
        """

        path = f"/api/static/airlines/{icao}/light"
        response = self._transport.request("GET", path)
        return AirlineLight(**response.json())
