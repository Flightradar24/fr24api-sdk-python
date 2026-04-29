# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Flight category enumeration for the Flightradar24 SDK."""

from enum import Enum
from typing import Literal

FlightCategoryCode = Literal[
    "P",
    "C",
    "M",
    "J",
    "T",
    "H",
    "B",
    "G",
    "D",
    "V",
    "O",
    "N",
]


class FlightCategory(str, Enum):
    """Aircraft / vehicle category codes used in API (e.g. flight summary).

    - **P** — **PASSENGER** — Commercial aircraft that carry passengers as their primary purpose.
    - **C** — **CARGO** — Aircraft that carry only cargo.
    - **M** — **MILITARY_AND_GOVERNMENT** — Aircraft operated by military or a governmental agency.
    - **J** — **BUSINESS_JETS** — Larger private aircraft, such as Gulfstream, Bombardier, and Pilatus.
    - **T** — **GENERAL_AVIATION** — Non-commercial transport flights, including private, ambulance,
      aerial survey, flight training and instrument calibration aircraft.
    - **H** — **HELICOPTERS** — Rotary wing aircraft.
    - **B** — **LIGHTER_THAN_AIR** — Lighter-than-air aircraft include gas-filled airships of all kinds.
    - **G** — **GLIDERS** — Unpowered aircraft.
    - **D** — **DRONES** — Uncrewed aircraft, ranging from small consumer drones to larger UAVs.
    - **V** — **GROUND_VEHICLES** — Transponder equipped vehicles, such as push-back tugs, fire trucks,
      and operations vehicles.
    - **O** — **OTHER** — Aircraft appearing on Flightradar24 not classified elsewhere
      (International Space Station, UFOs, Santa, etc).
    - **N** — **NON_CATEGORIZED** — Aircraft not yet placed into a category in the Flightradar24 database.
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


__all__ = ["FlightCategory", "FlightCategoryCode"]
