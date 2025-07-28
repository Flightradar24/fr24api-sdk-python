# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Resource class for flight summary data."""

from typing import Optional, Any, Annotated
from datetime import datetime
from pydantic import BaseModel, model_serializer, StringConstraints, Field

from ..transport import HttpTransport
from ..models.flight import (
    FlightSummaryLightResponse,
    FlightSummaryFullResponse,
    CountResponse,
)
from ..models.regex_patterns import (
    FLIGHT_NUMBER_PATTERN,
    CALLSIGN_PATTERN,
    REGISTRATION_PATTERN,
    AIRLINE_ICAO_PATTERN,
    AIRPORT_PARAM_PATTERN,
    ROUTE_PATTERN,
    SORT_PATTERN,
)


class _FlightSummaryParams(BaseModel):
    """Validate & serialise flight-summary query parameters."""

    flight_ids: Optional[list[str]] = Field(default=None, max_length=15)
    flight_datetime_from: Optional[datetime] = None
    flight_datetime_to: Optional[datetime] = None
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
    aircraft: Optional[list[str]] = Field(default=None, max_length=15)
    sort: Optional[Annotated[str, StringConstraints(pattern=SORT_PATTERN)]] = None
    limit: Optional[Annotated[int, Field(ge=1, le=20000)]] = None

    @model_serializer(mode="plain")
    def _to_query_dict(self) -> dict[str, Any]:
        query: dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if value is None:
                continue
            if isinstance(value, list):
                query[key] = ",".join(map(str, value))
            else:
                query[key] = str(value)
        return query


class FlightSummaryResource:
    """Provides access to flight-summary data.

    All parameters are **keyword-only** to keep the public surface explicit and
    IDE-discoverable.  Internally the parameters are validated and serialised
    via :class:`_FlightSummaryParams` – SDK users never deal with that class
    directly.
    """

    BASE_PATH = "/api/flight-summary"

    def __init__(self, transport: HttpTransport) -> None:
        self._transport = transport

    def get_light(
        self,
        *,
        flight_ids: Optional[list[str]] = None,
        flight_datetime_from: Optional[datetime] = None,
        flight_datetime_to: Optional[datetime] = None,
        flights: Optional[list[str]] = None,
        callsigns: Optional[list[str]] = None,
        registrations: Optional[list[str]] = None,
        painted_as: Optional[list[str]] = None,
        operating_as: Optional[list[str]] = None,
        airports: Optional[list[str]] = None,
        routes: Optional[list[str]] = None,
        aircraft: Optional[list[str]] = None,
        sort: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> FlightSummaryLightResponse:
        """Retrieve a lightweight summary of flights.

        Either ``flight_ids`` **or** a time-range (``flight_datetime_from`` and
        ``flight_datetime_to``) must be supplied, optionally combined with any
        other filters.
        """
        params = _FlightSummaryParams(
            flight_ids=flight_ids,
            flight_datetime_from=flight_datetime_from,
            flight_datetime_to=flight_datetime_to,
            flights=flights,
            callsigns=callsigns,
            registrations=registrations,
            painted_as=painted_as,
            operating_as=operating_as,
            airports=airports,
            routes=routes,
            aircraft=aircraft,
            sort=sort,
            limit=limit,
        ).model_dump(exclude_none=True)
        response = self._transport.request(
            "GET", f"{self.BASE_PATH}/light", params=params
        )
        return FlightSummaryLightResponse(**response.json())

    def get_full(
        self,
        *,
        flight_ids: Optional[list[str]] = None,
        flight_datetime_from: Optional[datetime] = None,
        flight_datetime_to: Optional[datetime] = None,
        flights: Optional[list[str]] = None,
        callsigns: Optional[list[str]] = None,
        registrations: Optional[list[str]] = None,
        painted_as: Optional[list[str]] = None,
        operating_as: Optional[list[str]] = None,
        airports: Optional[list[str]] = None,
        routes: Optional[list[str]] = None,
        aircraft: Optional[list[str]] = None,
        sort: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> FlightSummaryFullResponse:
        """Retrieve a full (detailed) summary of flights.

        The same parameter rules as :py:meth:`get_light` apply.
        """
        params = _FlightSummaryParams(
            flight_ids=flight_ids,
            flight_datetime_from=flight_datetime_from,
            flight_datetime_to=flight_datetime_to,
            flights=flights,
            callsigns=callsigns,
            registrations=registrations,
            painted_as=painted_as,
            operating_as=operating_as,
            airports=airports,
            routes=routes,
            aircraft=aircraft,
            sort=sort,
            limit=limit,
        ).model_dump(exclude_none=True)
        response = self._transport.request(
            "GET", f"{self.BASE_PATH}/full", params=params
        )
        return FlightSummaryFullResponse(**response.json())

    def count(
        self,
        *,
        flight_ids: Optional[list[str]] = None,
        flight_datetime_from: Optional[datetime] = None,
        flight_datetime_to: Optional[datetime] = None,
        flights: Optional[list[str]] = None,
        callsigns: Optional[list[str]] = None,
        registrations: Optional[list[str]] = None,
        painted_as: Optional[list[str]] = None,
        operating_as: Optional[list[str]] = None,
        airports: Optional[list[str]] = None,
        routes: Optional[list[str]] = None,
        aircraft: Optional[list[str]] = None,
    ) -> CountResponse:
        """Return the number of flight-summary records that match the filters.

        `sort` and `limit` are intentionally **not** accepted for this call
        because they are not meaningful for a count query.
        """
        params = _FlightSummaryParams(
            flight_ids=flight_ids,
            flight_datetime_from=flight_datetime_from,
            flight_datetime_to=flight_datetime_to,
            flights=flights,
            callsigns=callsigns,
            registrations=registrations,
            painted_as=painted_as,
            operating_as=operating_as,
            airports=airports,
            routes=routes,
            aircraft=aircraft,
        ).model_dump(exclude_none=True)
        response = self._transport.request(
            "GET", f"{self.BASE_PATH}/count", params=params
        )
        return CountResponse(**response.json())
