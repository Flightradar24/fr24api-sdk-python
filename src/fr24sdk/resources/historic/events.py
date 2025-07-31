# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Resource class for historic flight events data."""

from typing import Optional, Any
from pydantic import (
    BaseModel,
    Field,
    model_serializer,
    field_validator,
)

from ...transport import HttpTransport
from ...models.flight import (
    FlightEventsLightResponse,
    FlightEventsFullResponse,
)

# Valid event types for flight events
VALID_EVENT_TYPES = [
    "all",
    "gate_departure", 
    "takeoff",
    "cruising",
    "airspace_transition",
    "descent",
    "diverting",
    "diverted",
    "landed",
    "gate_arrival"
]


class _HistoricEventsParams(BaseModel):
    """Validate & serialise historic flight events query parameters."""

    flight_ids: list[str] = Field(..., description="fr24_ids (maximum 15 IDs)", max_length=15)
    event_types: list[str] = Field(..., description="Event types to filter by (comma-separated values or list)")


    @field_validator("event_types")
    @classmethod
    def validate_event_types(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        if v is None:
            return v
        
        for event_type in v:
            if event_type not in VALID_EVENT_TYPES:
                raise ValueError(f"Invalid event type '{event_type}'. Valid types: {', '.join(VALID_EVENT_TYPES)}")
        
        return v

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


class HistoricEventsResource:
    """Provides access to historic flight events data."""

    BASE_PATH = "/api/historic/flight-events"

    def __init__(self, transport: HttpTransport):
        self._transport = transport

    def get_light(
        self,
        flight_ids: list[str],
        event_types: list[str],
    ) -> FlightEventsLightResponse:
        """Returns comprehensive historical information on flight events including takeoff, landing, 
        gate movements, and airspace transitions.

        Args:
            flight_ids: Flight IDs to filter by. ["391fdd79", "35f2ffd9"]. Maximum 15 IDs allowed.
            event_types: List of event types like ["gate_departure", "takeoff"]
                Available values: all, gate_departure, takeoff, cruising, airspace_transition, descent, landed, gate_arrival.
        """
        params = _HistoricEventsParams(
            flight_ids=flight_ids,
            event_types=event_types,
        ).model_dump(exclude_none=True)
        response = self._transport.request(
            "GET", f"{self.BASE_PATH}/light", params=params
        )
        return FlightEventsLightResponse(**response.json())

    def get_full(
        self,
        flight_ids: list[str],
        event_types: list[str],
    ) -> FlightEventsFullResponse:
        """Returns comprehensive historical information on flight events including takeoff, landing,
        gate movements, and airspace transitions, with additional flight and aircraft details such as 
        origin, destination, and aircraft type.

        Args:
            flight_ids: Flight IDs to filter by. ["391fdd79", "35f2ffd9"]. Maximum 15 IDs allowed.
            event_types: List of event types like ["gate_departure", "takeoff"].
                Available values: all, gate_departure, takeoff, cruising, airspace_transition, descent, landed, gate_arrival.
        """
        params = _HistoricEventsParams(
            flight_ids=flight_ids,
            event_types=event_types,
        ).model_dump(exclude_none=True)
        response = self._transport.request(
            "GET", f"{self.BASE_PATH}/full", params=params
        )
        return FlightEventsFullResponse(**response.json())
