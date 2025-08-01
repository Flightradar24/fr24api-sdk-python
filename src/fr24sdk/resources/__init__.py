# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Exposes resource classes for different API categories."""

from ..transport import HttpTransport
from .airlines import AirlinesResource
from .airports import AirportsResource
from .flight_summary import FlightSummaryResource
from .flight_tracks import FlightTracksResource
from .usage import UsageResource

from .live.positions import LivePositionsResource
from .historic.positions import HistoricPositionsResource
from .historic.events import HistoricEventsResource

class LiveResource:
    """Namespace for live data resources."""

    def __init__(self, transport: HttpTransport):
        self.flight_positions = LivePositionsResource(transport)


class HistoricResource:
    """Namespace for historic data resources."""

    def __init__(self, transport: HttpTransport):
        self.flight_positions = HistoricPositionsResource(transport)
        self.flight_events = HistoricEventsResource(transport)

__all__ = [
    "AirlinesResource",
    "AirportsResource",
    "FlightSummaryResource",
    "FlightTracksResource",
    "UsageResource",
    "LiveResource",
    "HistoricResource",
    "LivePositionsResource",
    "HistoricPositionsResource",
    "HistoricEventsResource",
]
