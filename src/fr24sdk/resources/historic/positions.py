# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Resource class for historic flight position data."""

from typing import Optional, Any, Annotated, Union
from datetime import datetime, timezone
from pydantic import (
    BaseModel,
    StringConstraints,
    Field,
    model_serializer,
    field_validator,
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

# Min timestamp: 2016-05-11 00:00:00 UTC
MIN_HISTORIC_DATETIME = datetime(2016, 5, 11, 0, 0, 0, tzinfo=timezone.utc)


class _HistoricPositionsParams(BaseModel):
    """Validate & serialise historic-positions query parameters."""

    timestamp: Union[int, datetime]
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
    gspeed: Optional[Union[Annotated[int, Field(ge=0, le=5000)], str]] = None
    limit: Optional[Annotated[int, Field(ge=1, le=30000)]] = None

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: Union[int, datetime]) -> int:
        if isinstance(v, datetime):
            # If datetime has no timezone info, treat it as UTC
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            timestamp_value = int(v.timestamp())
        else:
            timestamp_value = v

        # Validate the timestamp is after FR24 API Flight Positions History minimum date
        if timestamp_value < int(MIN_HISTORIC_DATETIME.timestamp()):
            raise ValueError(
                f"Timestamp must be after {MIN_HISTORIC_DATETIME.isoformat()}"
            )

        return timestamp_value

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
                query[key] = value
        return query


class HistoricPositionsResource:
    """Provides access to historic flight position data."""

    BASE_PATH = "/api/historic/flight-positions"

    def __init__(self, transport: HttpTransport):
        self._transport = transport

    def get_light(
        self,
        timestamp: Union[int, datetime],
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
        limit: Optional[int] = None,
    ) -> FlightPositionsLightResponse:
        """Returns comprehensive historical information on aircraft flight movements, including flight and aircraft details such as origin, destination, and aircraft type, dating back to May 11, 2016. At least one query parameter and a history snapshot timestamp are required to retrieve data.

        Requires a timestamp and at least one other filter parameter (e.g., bounds, flights).
        The timestamp can be either a datetime object or a UNIX timestamp integer.
        """
        params = _HistoricPositionsParams(
            timestamp=timestamp,
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
            limit=limit,
        ).model_dump(exclude_none=True)
        response = self._transport.request(
            "GET", f"{self.BASE_PATH}/light", params=params
        )
        return FlightPositionsLightResponse(**response.json())

    def get_full(
        self,
        timestamp: Union[int, datetime],
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
        limit: Optional[int] = None,
    ) -> FlightPositionsFullResponse:
        """Returns comprehensive historical information on aircraft flight movements, including flight and aircraft details such as origin, destination, and aircraft type, dating back to May 11, 2016. At least one query parameter and a history snapshot timestamp are required to retrieve data.

        Requires a timestamp and at least one other filter parameter (e.g., bounds, flights).
        The timestamp can be either a datetime object or a UNIX timestamp integer.
        """
        params = _HistoricPositionsParams(
            timestamp=timestamp,
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
            limit=limit,
        ).model_dump(exclude_none=True)
        response = self._transport.request(
            "GET", f"{self.BASE_PATH}/full", params=params
        )
        return FlightPositionsFullResponse(**response.json())

    def count(
        self,
        timestamp: Union[int, datetime],
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
        """Get count of historical flight positions.

        Requires a timestamp and at least one other filter parameter (e.g., bounds, flights).
        The timestamp can be either a datetime object or a UNIX timestamp integer.
        """
        params = _HistoricPositionsParams(
            timestamp=timestamp,
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
