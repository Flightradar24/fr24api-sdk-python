# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Data models for airport information."""

from pydantic import BaseModel
from typing import Optional


class Timezone(BaseModel):
    """Represents timezone information."""

    name: str
    offset: int


class Country(BaseModel):
    """Represents country information."""

    code: str
    name: str


class Surface(BaseModel):
    """Represents runway surface information."""

    type: str
    description: str


class Runway(BaseModel):
    """Represents runway information."""

    designator: str
    heading: int
    length: int
    width: int
    elevation: int
    thr_coordinates: list[float]
    surface: Surface


class AirportLight(BaseModel):
    """Basic airport information."""

    icao: str
    iata: Optional[str] = None
    name: Optional[str] = None


class AirportFull(BaseModel):
    """Detailed airport information."""

    name: str
    lat: float
    lon: float
    elevation: float
    country: Country
    city: str
    timezone: Timezone
    iata: Optional[str] = None
    icao: Optional[str] = None
    state: Optional[str] = None
    runways: Optional[list[Runway]] = None
