# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Resource class for interacting with airport-related API endpoints."""

from typing import Optional, Annotated
from pydantic import StringConstraints

from ..transport import HttpTransport
from ..models.airport import AirportLight, AirportFull
from ..models.regex_patterns import AIRPORT_CODE_PATTERN

class AirportsResource:
    """Provides access to airport data."""

    def __init__(self, transport: HttpTransport):
        self._transport = transport

    def get_light(self, code: Annotated[str, StringConstraints(pattern=AIRPORT_CODE_PATTERN)]) -> Optional[AirportLight]:
        """Get basic airport information by IATA or ICAO code.

        Args:
            code: Airport IATA or ICAO code (e.g., "LHR", "EGLL").

        Returns:
            An AirportLight object if found. Raises NotFoundError if not found.
        """
        path = f"/api/static/airports/{code}/light"
        response = self._transport.request("GET", path)
        return AirportLight(**response.json())

    def get_full(self, code: Annotated[str, StringConstraints(pattern=AIRPORT_CODE_PATTERN)]) -> Optional[AirportFull]:
        """Get detailed airport information by IATA or ICAO code.

        Args:
            code: Airport IATA or ICAO code (e.g., "WAW", "EPWA").

        Returns:
            An AirportFull object if found. Raises NotFoundError if not found.
        """
        path = f"/api/static/airports/{code}/full"
        response = self._transport.request("GET", path)
        return AirportFull(**response.json())
