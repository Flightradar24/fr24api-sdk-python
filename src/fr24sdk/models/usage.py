# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Data models for API usage information."""

from pydantic import BaseModel, Field


class UsageLogSummary(BaseModel):
    """Summary of API usage for a specific endpoint."""

    endpoint: str
    request_count: int
    credits: int


class UsageLogSummaryResponse(BaseModel):
    data: list[UsageLogSummary] = Field(default_factory=list)
