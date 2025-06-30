# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Geographic and aviation-specific data types for the FR24 API."""

from pydantic import BaseModel, Field, model_validator


class Boundary(BaseModel):
    """Represents a geographic bounding box.

    Args:
        north: Northern latitude boundary (-90.0 to 90.0)
        south: Southern latitude boundary (-90.0 to 90.0)
        west: Western longitude boundary (-180.0 to 180.0)
        east: Eastern longitude boundary (-180.0 to 180.0)
    """

    north: float = Field(
        ..., ge=-90.0, le=90.0, description="Northern latitude boundary"
    )
    south: float = Field(
        ..., ge=-90.0, le=90.0, description="Southern latitude boundary"
    )
    west: float = Field(
        ..., ge=-180.0, le=180.0, description="Western longitude boundary"
    )
    east: float = Field(
        ..., ge=-180.0, le=180.0, description="Eastern longitude boundary"
    )

    @model_validator(mode="after")
    def validate_boundary_logic(self):
        """Validate that north > south."""
        if self.north <= self.south:
            raise ValueError(
                f"North latitude ({self.north}) must be greater than south latitude ({self.south})"
            )
        return self

    def to_string(self) -> str:
        """Convert boundary to FR24 API string format: 'north,south,west,east'."""
        return f"{self.north},{self.south},{self.west},{self.east}"

    def __str__(self) -> str:
        """String representation using the FR24 API format."""
        return self.to_string()

    @classmethod
    def from_string(cls, bounds_str: str) -> "Boundary":
        """Create Boundary from FR24 API string format: 'north,south,west,east'."""
        parts = bounds_str.split(",")
        if len(parts) != 4:
            raise ValueError(
                "Boundary string must have exactly 4 comma-separated values"
            )
        north, south, west, east = map(float, parts)
        return cls(north=north, south=south, west=west, east=east)


class AltitudeRange(BaseModel):
    """Represents an altitude range in feet.

    Args:
        min_altitude: Minimum altitude in feet (>= -2000)
        max_altitude: Maximum altitude in feet (>= min_altitude)
    """

    min_altitude: int = Field(..., ge=-2000, description="Minimum altitude in feet")
    max_altitude: int = Field(..., ge=0, description="Maximum altitude in feet")

    @model_validator(mode="after")
    def validate_altitude_range(self):
        """Validate that min_altitude <= max_altitude."""
        if self.min_altitude > self.max_altitude:
            raise ValueError(
                f"Minimum altitude ({self.min_altitude}) must be <= maximum altitude ({self.max_altitude})"
            )
        return self

    def to_string(self) -> str:
        """Convert altitude range to FR24 API string format: 'min-max'."""
        return f"{self.min_altitude}-{self.max_altitude}"

    def __str__(self) -> str:
        """String representation using the FR24 API format."""
        return self.to_string()

    @classmethod
    def from_string(cls, range_str: str) -> "AltitudeRange":
        """Create AltitudeRange from FR24 API string format: 'min-max'."""
        parts = range_str.split("-")
        if len(parts) != 2:
            raise ValueError(
                "Altitude range string must have exactly 2 dash-separated values"
            )
        min_alt, max_alt = map(int, parts)
        return cls(min_altitude=min_alt, max_altitude=max_alt)
