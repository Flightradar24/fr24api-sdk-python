# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Resource class for live flight position data."""

from typing import Optional, Any, Annotated, Union
from pydantic import (
    BaseModel,
    StringConstraints,
    Field,
    model_serializer,
)

from ...transport import HttpTransport
from ...models.flight import (
    FlightPositionsLightResponse,
    FlightPositionsFullResponse,
    CountResponse,
)
from ...models.geographic import (
    Boundary,
    AltitudeRange,
)
from ...models.regex_patterns import (
    FLIGHT_NUMBER_PATTERN,
    CALLSIGN_PATTERN,
    REGISTRATION_PATTERN,
    AIRLINE_ICAO_PATTERN,
    AIRPORT_PARAM_PATTERN,
    ROUTE_PATTERN,
    SQUAWK_PATTERN,
    SERVICE_TYPES_PATTERN,
    DATA_SOURCE_PATTERN,
)


class _LivePositionsParams(BaseModel):
    """Validate & serialise live-positions query parameters."""

    bounds: Optional[Union[Boundary, str]] = None
    flights: Optional[
        list[Annotated[str, StringConstraints(pattern=FLIGHT_NUMBER_PATTERN)]]
    ] = Field(default=None, max_length=15)
    callsigns: Optional[
        list[Annotated[str, StringConstraints(pattern=CALLSIGN_PATTERN)]]
    ] = Field(default=None, max_length=15)
    registrations: Optional[
        list[Annotated[str, StringConstraints(pattern=REGISTRATION_PATTERN)]]
    ] = Field(default=None, max_length=15)
    painted_as: Optional[
        list[Annotated[str, StringConstraints(pattern=AIRLINE_ICAO_PATTERN)]]
    ] = Field(default=None, max_length=15)
    operating_as: Optional[
        list[Annotated[str, StringConstraints(pattern=AIRLINE_ICAO_PATTERN)]]
    ] = Field(default=None, max_length=15)
    airports: Optional[
        list[Annotated[str, StringConstraints(pattern=AIRPORT_PARAM_PATTERN)]]
    ] = Field(default=None, max_length=15)
    routes: Optional[list[Annotated[str, StringConstraints(pattern=ROUTE_PATTERN)]]] = (
        Field(default=None, max_length=15)
    )
    aircraft: Optional[str] = None
    altitude_ranges: Annotated[
        Optional[list[Union[AltitudeRange, str]]], Field(default=None, max_length=15)
    ] = None
    squawks: Optional[
        list[Annotated[str, StringConstraints(pattern=SQUAWK_PATTERN)]]
    ] = Field(default=None, max_length=15)
    categories: Optional[
        list[Annotated[str, StringConstraints(pattern=SERVICE_TYPES_PATTERN)]]
    ] = Field(default=None, max_length=15)
    data_sources: Optional[
        list[Annotated[str, StringConstraints(pattern=DATA_SOURCE_PATTERN)]]
    ] = Field(default=None, max_length=15)
    airspaces: Optional[list[str]] = Field(default=None, max_length=15)
    gspeed: Optional[Union[Annotated[int, Field(ge=0, le=5000)], str]] = None
    limit: Optional[Annotated[int, Field(ge=1, le=30000)]] = None

    @model_serializer(mode="plain")
    def _to_query_dict(self) -> dict[str, Any]:
        """Convert model to query dictionary, excluding None values."""
        query: dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if value is None:
                continue
            if isinstance(value, list):
                query[key] = ",".join(map(str, value))
            else:
                query[key] = str(value)
        return query


class LivePositionsResource:
    """Provides access to live flight position data."""

    BASE_PATH = "/api/live/flight-positions"

    def __init__(self, transport: HttpTransport):
        self._transport = transport

    def get_light(
        self,
        bounds: Optional[Union[Boundary, str]] = None,
        flights: Optional[list[str]] = None,
        callsigns: Optional[list[str]] = None,
        registrations: Optional[list[str]] = None,
        painted_as: Optional[list[str]] = None,
        operating_as: Optional[list[str]] = None,
        airports: Optional[list[str]] = None,
        routes: Optional[list[str]] = None,
        aircraft: Optional[str] = None,
        altitude_ranges: Optional[list[Union[AltitudeRange, str]]] = None,
        squawks: Optional[list[str]] = None,
        categories: Optional[list[str]] = None,
        data_sources: Optional[list[str]] = None,
        airspaces: Optional[list[str]] = None,
        gspeed: Optional[Union[int, str]] = None,
        limit: Optional[int] = None,
    ) -> FlightPositionsLightResponse:
        """Returns real-time information on aircraft flight movements including latitude, longitude, speed, and altitude. At least one query parameter is required to retrieve data.
        Requires at least one filter parameter (e.g., bounds, flights).
        """
        params = _LivePositionsParams(
            bounds=bounds,
            flights=flights,
            callsigns=callsigns,
            registrations=registrations,
            painted_as=painted_as,
            operating_as=operating_as,
            airports=airports,
            routes=routes,
            aircraft=aircraft,
            altitude_ranges=altitude_ranges,
            squawks=squawks,
            categories=categories,
            data_sources=data_sources,
            airspaces=airspaces,
            gspeed=gspeed,
            limit=limit,
        ).model_dump(exclude_none=True)
        response = self._transport.request(
            "GET", f"{self.BASE_PATH}/light", params=params
        )
        return FlightPositionsLightResponse(**response.json())

    def get_full(
        self,
        bounds: Optional[Union[Boundary, str]] = None,
        flights: Optional[list[str]] = None,
        callsigns: Optional[list[str]] = None,
        registrations: Optional[list[str]] = None,
        painted_as: Optional[list[str]] = None,
        operating_as: Optional[list[str]] = None,
        airports: Optional[list[str]] = None,
        routes: Optional[list[str]] = None,
        aircraft: Optional[str] = None,
        altitude_ranges: Optional[list[Union[AltitudeRange, str]]] = None,
        squawks: Optional[list[str]] = None,
        categories: Optional[list[str]] = None,
        data_sources: Optional[list[str]] = None,
        airspaces: Optional[list[str]] = None,
        gspeed: Optional[Union[int, str]] = None,
        limit: Optional[int] = None,
    ) -> FlightPositionsFullResponse:
        """Returns comprehensive real-time information on aircraft flight movements, including flight and aircraft details such as origin, destination, and aircraft type. At least one query parameter is required to retrieve data
        Requires at least one filter parameter (e.g., bounds, flights).
        """
        params = _LivePositionsParams(
            bounds=bounds,
            flights=flights,
            callsigns=callsigns,
            registrations=registrations,
            painted_as=painted_as,
            operating_as=operating_as,
            airports=airports,
            routes=routes,
            aircraft=aircraft,
            altitude_ranges=altitude_ranges,
            squawks=squawks,
            categories=categories,
            data_sources=data_sources,
            airspaces=airspaces,
            gspeed=gspeed,
            limit=limit,
        ).model_dump(exclude_none=True)
        response = self._transport.request(
            "GET", f"{self.BASE_PATH}/full", params=params
        )
        return FlightPositionsFullResponse(**response.json())

    def count(
        self,
        bounds: Optional[Union[Boundary, str]] = None,
        flights: Optional[list[str]] = None,
        callsigns: Optional[list[str]] = None,
        registrations: Optional[list[str]] = None,
        painted_as: Optional[list[str]] = None,
        operating_as: Optional[list[str]] = None,
        airports: Optional[list[str]] = None,
        routes: Optional[list[str]] = None,
        aircraft: Optional[str] = None,
        altitude_ranges: Optional[list[Union[AltitudeRange, str]]] = None,
        squawks: Optional[list[str]] = None,
        categories: Optional[list[str]] = None,
        data_sources: Optional[list[str]] = None,
        gspeed: Optional[Union[int, str]] = None,
    ) -> CountResponse:
        """Get count of live flight positions.

        Requires at least one filter parameter (e.g., bounds, flights).
        The 'airspaces' parameter is not applicable to the count endpoint.
        """
        params = _LivePositionsParams(
            bounds=bounds,
            flights=flights,
            callsigns=callsigns,
            registrations=registrations,
            painted_as=painted_as,
            operating_as=operating_as,
            airports=airports,
            routes=routes,
            aircraft=aircraft,
            altitude_ranges=altitude_ranges,
            squawks=squawks,
            categories=categories,
            data_sources=data_sources,
            gspeed=gspeed,
        ).model_dump(exclude_none=True)
        response = self._transport.request(
            "GET", f"{self.BASE_PATH}/count", params=params
        )
        return CountResponse(**response.json())
