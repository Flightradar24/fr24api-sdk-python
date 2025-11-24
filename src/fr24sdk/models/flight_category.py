# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Flight category enumeration for the Flightradar24 SDK."""

from enum import Enum


class FlightCategory(str, Enum):
    """Enumeration of FlightRadar24 flight categories.
    
    Maps character literals used by the FR24 API to identify different
    types of aircraft and flight operations.
    """
    
    PASSENGER = "P"
    CARGO = "C"
    MILITARY_AND_GOVERNMENT = "M"
    BUSINESS_JETS = "J"
    GENERAL_AVIATION = "T"
    HELICOPTERS = "H"
    LIGHTER_THAN_AIR = "B"
    GLIDERS = "G"
    DRONES = "D"
    GROUND_VEHICLES = "V"
    OTHER = "O"
    NON_CATEGORIZED = "N"

    def __str__(self) -> str:
        return self.value
