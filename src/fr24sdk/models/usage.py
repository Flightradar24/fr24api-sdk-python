# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Data models for API usage information."""

from dataclasses import dataclass, field


@dataclass
class UsageLogSummary:
    """Summary of API usage for a specific endpoint."""

    endpoint: str
    request_count: int
    credits: int


@dataclass
class UsageLogSummaryResponse:
    data: list[UsageLogSummary] = field(default_factory=list)
