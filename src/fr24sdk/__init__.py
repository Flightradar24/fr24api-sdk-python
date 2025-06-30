# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Flightradar24 API SDK for Python."""

__version__ = "0.1.0"

from .client import Client

# from .async_client import AsyncClient # To be added later
from .exceptions import (
    Fr24SdkError,
    TransportError,
    ApiError,
    AuthenticationError,
    RateLimitError,
    PaymentRequiredError,
    BadRequestError,
    NotFoundError,
)

__all__ = [
    "Client",
    # "AsyncClient",
    "Fr24SdkError",
    "TransportError",
    "ApiError",
    "AuthenticationError",
    "RateLimitError",
    "PaymentRequiredError",
    "BadRequestError",
    "NotFoundError",
    "__version__",
]
