# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Resource class for API usage data."""

from ..transport import HttpTransport
from ..models.usage import UsageLogSummaryResponse


class UsageResource:
    """Provides access to API usage data."""

    BASE_PATH = "/api/usage"

    def __init__(self, transport: HttpTransport):
        self._transport = transport

    def get(self, period: str = "24h") -> UsageLogSummaryResponse:
        """Get info on API account usage.

        Args:
            period: Time period for usage summary.
                    Enum: "24h", "7d", "30d", "1y". Default: "24h".

        Returns:
            A UsageLogSummaryResponse object.
        """
        response = self._transport.request(
            "GET", self.BASE_PATH, params={"period": period}
        )
        return UsageLogSummaryResponse(**response.json())
