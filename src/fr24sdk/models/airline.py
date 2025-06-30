# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Data models for airline information."""

from pydantic import BaseModel
from typing import Optional


class AirlineLight(BaseModel):
    """Basic airline information."""

    name: str
    icao: str
    iata: Optional[str] = None
