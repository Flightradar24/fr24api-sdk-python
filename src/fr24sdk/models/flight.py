# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
# Note: Refer to Flightradar24 API documentation for more information on the fields.
"""Data models for flight information, positions, summaries, and tracks."""

from typing import Optional, Union
from pydantic import BaseModel, Field


class FlightPositionsLight(BaseModel):
    """Lightweight real-time flight position data."""

    fr24_id: str
    lat: float
    lon: float
    track: int
    alt: int
    gspeed: int
    vspeed: int
    squawk: str  # Spec says string, example has int-like string
    timestamp: str  # ISO 8601 date-time string
    source: str
    hex: Optional[str] = None
    callsign: Optional[str] = None


class FlightPositionsLightResponse(BaseModel):
    data: Optional[list[FlightPositionsLight]] = Field(default_factory=list)


class FlightPositionsFull(BaseModel):
    """Detailed real-time or historical flight position data."""

    fr24_id: str
    lat: float
    lon: float
    track: int
    alt: int
    gspeed: int
    vspeed: int
    squawk: str
    timestamp: str  # ISO 8601 date-time string
    source: str
    flight: Optional[str] = None
    callsign: Optional[str] = None
    hex: Optional[str] = None
    type: Optional[str] = None  # Aircraft ICAO type
    reg: Optional[str] = None  # Aircraft registration
    painted_as: Optional[str] = None  # Airline ICAO
    operating_as: Optional[str] = None  # Airline ICAO
    orig_iata: Optional[str] = None
    orig_icao: Optional[str] = None
    dest_iata: Optional[str] = None
    dest_icao: Optional[str] = None
    eta: Optional[str] = None  # ISO 8601 date-time string


class FlightPositionsFullResponse(BaseModel):
    data: Optional[list[FlightPositionsFull]] = Field(default_factory=list)


class FlightSummaryLight(BaseModel):
    """Lightweight flight summary data."""

    fr24_id: str
    flight: Optional[str] = None
    callsign: Optional[str] = None
    operating_as: Optional[str] = None
    painted_as: Optional[str] = None
    type: Optional[str] = None
    reg: Optional[str] = None
    orig_icao: Optional[str] = None
    datetime_takeoff: Optional[str] = None  # YYYY-MM-DDTHH:MM:SS
    dest_icao: Optional[str] = None
    dest_icao_actual: Optional[str] = None
    datetime_landed: Optional[str] = None  # YYYY-MM-DDTHH:MM:SS
    hex: Optional[str] = None
    first_seen: Optional[str] = None  # YYYY-MM-DDTHH:MM:SS
    last_seen: Optional[str] = None  # YYYY-MM-DDTHH:MM:SS
    flight_ended: Optional[bool] = None


class FlightSummaryLightResponse(BaseModel):
    data: Optional[list[FlightSummaryLight]] = Field(default_factory=list)


class FlightSummaryFull(BaseModel):
    """Detailed flight summary data."""

    fr24_id: str
    flight: Optional[str] = None
    callsign: Optional[str] = None
    operating_as: Optional[str] = None
    painted_as: Optional[str] = None
    type: Optional[str] = None
    reg: Optional[str] = None
    orig_icao: Optional[str] = None
    orig_iata: Optional[str] = None
    datetime_takeoff: Optional[str] = None
    runway_takeoff: Optional[str] = None
    dest_icao: Optional[str] = None
    dest_iata: Optional[str] = None
    dest_icao_actual: Optional[str] = None
    dest_iata_actual: Optional[str] = None
    datetime_landed: Optional[str] = None
    runway_landed: Optional[str] = None
    flight_time: Optional[float] = None  # seconds
    actual_distance: Optional[float] = None  # km
    circle_distance: Optional[float] = None  # km
    category: Optional[str] = None
    hex: Optional[str] = None
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    flight_ended: Optional[bool] = None


class FlightSummaryFullResponse(BaseModel):
    data: Optional[list[FlightSummaryFull]] = Field(default_factory=list)


class FlightTrackPoint(BaseModel):
    """A single point in a flight's track."""

    timestamp: str  # ISO 8601 date-time string
    lat: float
    lon: float
    alt: int
    gspeed: int
    vspeed: int
    track: int
    squawk: str
    callsign: Optional[str] = None
    source: str


class FlightTracks(BaseModel):
    """Positional tracks for a specific flight."""

    fr24_id: str
    tracks: Optional[list[FlightTrackPoint]] = Field(default_factory=list)


class FlightTracksResponse(BaseModel):
    data: Optional[list[FlightTracks]] = Field(default_factory=list)


class CountResponse(BaseModel):
    """Generic count response."""

    record_count: int


# Flight Events Models

class GateDetails(BaseModel):
    """Gate-related details for gate departure/arrival events."""
    
    gate_ident: Optional[str] = None
    gate_lat: Optional[float] = None
    gate_lon: Optional[float] = None


class LandingDetails(BaseModel):
    """Runway-related details for landing events."""

    landed_icao: Optional[str] = None
    landed_runway: Optional[str] = None


class TakeoffDetails(BaseModel):
    """Takeoff-related details for takeoff events."""

    takeoff_runway: Optional[str] = None


class AirspaceDetails(BaseModel):
    """Airspace transition details."""
    
    exited_airspace: Optional[str] = None
    exited_airspace_id: Optional[str] = None
    entered_airspace: Optional[str] = None
    entered_airspace_id: Optional[str] = None


class FlightEvent(BaseModel):
    """A single flight event with optional position and details."""
    
    type: str  # event type
    timestamp: str  # ISO 8601 date-time string
    lat: Optional[float] = None
    lon: Optional[float] = None
    alt: Optional[int] = None
    gspeed: Optional[int] = None
    details: Optional[Union[GateDetails, TakeoffDetails, LandingDetails, AirspaceDetails]] = None 


class FlightEventsLight(BaseModel):
    """Lightweight flight events data."""
    
    fr24_id: str
    callsign: Optional[str] = None
    hex: Optional[str] = None
    events: Optional[list[FlightEvent]] = Field(default_factory=list)


class FlightEventsLightResponse(BaseModel):
    data: Optional[list[FlightEventsLight]] = Field(default_factory=list)


class FlightEventsFull(BaseModel):
    """Full flight events data with additional flight information."""
    
    fr24_id: str
    callsign: Optional[str] = None
    hex: Optional[str] = None
    operating_as: Optional[str] = None
    painted_as: Optional[str] = None
    orig_iata: Optional[str] = None
    orig_icao: Optional[str] = None
    dest_iata: Optional[str] = None
    dest_icao: Optional[str] = None
    events: Optional[list[FlightEvent]] = Field(default_factory=list)


class FlightEventsFullResponse(BaseModel):
    data: Optional[list[FlightEventsFull]] = Field(default_factory=list)
