# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Unit tests for the live_positions module."""

import pytest
from unittest.mock import Mock, MagicMock

from fr24sdk.resources.live.positions import (
    LivePositionsResource,
    _LivePositionsParams,
)
from fr24sdk.models.flight import (
    FlightPositionsLightResponse,
    FlightPositionsFullResponse,
    CountResponse,
)
from fr24sdk.transport import HttpTransport


class TestLivePositionsParams:
    """Test the _LivePositionsParams class."""

    def test_serialize_params(self):
        """Test parameters are correctly serialized for API requests."""
        # Test with various parameter types
        params = _LivePositionsParams(
            bounds="10,20,30,40",
            flights=["BA1234", "LH5678"],
            callsigns=["BAW123"],
            altitude_ranges=["1000,5000", "10000,20000"],
            limit=100,
        )

        serialized = params._to_query_dict()

        # Check serialization results
        assert serialized["bounds"] == "10,20,30,40"
        assert serialized["flights"] == "BA1234,LH5678"
        assert serialized["callsigns"] == "BAW123"
        assert serialized["altitude_ranges"] == "1000,5000,10000,20000"
        assert serialized["limit"] == '100'

        # Check that None values are not included
        assert "registrations" not in serialized


class TestLivePositionsResource:
    """Test the LivePositionsResource class."""

    @pytest.fixture
    def mock_transport(self):
        """Create a mock transport."""
        mock = Mock(spec=HttpTransport)
        return mock

    @pytest.fixture
    def live_positions(self, mock_transport):
        """Create a LivePositionsResource with mock transport."""
        return LivePositionsResource(mock_transport)

    def test_get_light_success(self, live_positions, mock_transport):
        """Test successful get_light call."""
        # Mock response data

        # Configure mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "fr24_id": "123456",
                    "lat": 51.5,
                    "lon": -0.1,
                    "track": 90,
                    "alt": 35000,
                    "gspeed": 500,
                    "vspeed": 0,
                    "squawk": "1234",
                    "timestamp": "2023-01-01T12:00:00Z",
                    "source": "ADSB",
                }
            ]
        }
        mock_transport.request.return_value = mock_response

        # Call the method
        result = live_positions.get_light(bounds="10,20,30,40", flights=["BA1234"])

        # Verify results
        assert isinstance(result, FlightPositionsLightResponse)
        assert len(result.data) == 1
        assert result.data[0].fr24_id == "123456"
        assert result.data[0].lat == 51.5
        assert result.data[0].lon == -0.1

        # Verify mock was called correctly
        mock_transport.request.assert_called_once()
        args, kwargs = mock_transport.request.call_args
        assert args[0] == "GET"
        assert args[1] == "/api/live/flight-positions/light"
        assert "bounds" in kwargs["params"]
        assert kwargs["params"]["bounds"] == "10,20,30,40"

    def test_get_light_empty_response(self, live_positions, mock_transport):
        """Test get_light with empty response."""
        # Mock empty response
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_transport.request.return_value = mock_response

        # Call method
        result = live_positions.get_light(bounds="10,20,30,40")

        # Verify empty result
        assert isinstance(result, FlightPositionsLightResponse)
        assert len(result.data) == 0

    def test_get_full_success(self, live_positions, mock_transport):
        """Test successful get_full call."""
        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "fr24_id": "123456",
                    "lat": 51.5,
                    "lon": -0.1,
                    "track": 90,
                    "alt": 35000,
                    "gspeed": 500,
                    "vspeed": 0,
                    "squawk": "1234",
                    "timestamp": "2023-01-01T12:00:00Z",
                    "source": "ADSB",
                    "flight": "BA1234",
                    "callsign": "BAW123",
                    "type": "B738",
                    "reg": "G-ABCD",
                    "orig_icao": "EGLL",
                    "dest_icao": "EGCC",
                }
            ]
        }
        mock_transport.request.return_value = mock_response

        # Call the method
        result = live_positions.get_full(bounds="10,20,30,40", flights=["BA1234"])

        # Verify results
        assert isinstance(result, FlightPositionsFullResponse)
        assert len(result.data) == 1
        assert result.data[0].fr24_id == "123456"
        assert result.data[0].flight == "BA1234"
        assert result.data[0].type == "B738"

        # Verify mock was called correctly
        mock_transport.request.assert_called_once()
        args, kwargs = mock_transport.request.call_args
        assert args[0] == "GET"
        assert args[1] == "/api/live/flight-positions/full"

    def test_get_full_empty_response(self, live_positions, mock_transport):
        """Test get_full with empty response."""
        # Mock empty response
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_transport.request.return_value = mock_response

        # Call method
        result = live_positions.get_full(bounds="10,20,30,40")

        # Verify empty result
        assert isinstance(result, FlightPositionsFullResponse)
        assert len(result.data) == 0

    def test_count_success(self, live_positions, mock_transport):
        """Test successful count call."""
        # Mock response data
        response_data = {"record_count": 42}

        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = response_data
        mock_transport.request.return_value = mock_response

        # Call the method
        result = live_positions.count(bounds="10,20,30,40")

        # Verify results
        assert isinstance(result, CountResponse)
        assert result.record_count == 42

        # Verify mock was called correctly
        mock_transport.request.assert_called_once()
        args, kwargs = mock_transport.request.call_args
        assert args[0] == "GET"
        assert args[1] == "/api/live/flight-positions/count"

    def test_with_airspaces_parameter(self, live_positions, mock_transport):
        """Test methods with the airspaces parameter."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_transport.request.return_value = mock_response

        # Call with airspaces parameter
        live_positions.get_light(airspaces=["EGTT"])

        # Verify parameter was correctly passed
        args, kwargs = mock_transport.request.call_args
        params = kwargs["params"]
        assert "airspaces" in params
        assert params["airspaces"] == "EGTT"

    def test_with_all_parameters(self, live_positions, mock_transport):
        """Test a call with all possible parameters."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_transport.request.return_value = mock_response

        # Call with all parameters
        live_positions.get_light(
            bounds="10,20,30,40",
            flights=["BA1234", "LH5678"],
            callsigns=["BAW123"],
            registrations=["G-ABCD"],
            painted_as=["DLH"],
            operating_as=["BAW"],
            airports=["EGLL"],
            routes=["EGLL-EGCC"],
            aircraft="B738",
            altitude_ranges=["1000,5000"],
            squawks=["1234"],
            categories=["P"],
            data_sources=["ADSB"],
            airspaces=["EGTT"],
            gspeed=500,
            limit=100,
        )

        # Verify parameters were correctly passed
        args, kwargs = mock_transport.request.call_args
        params = kwargs["params"]

        # Check all parameters are included
        assert "bounds" in params
        assert "flights" in params
        assert "callsigns" in params
        assert "registrations" in params
        assert "painted_as" in params
        assert "operating_as" in params
        assert "airports" in params
        assert "routes" in params
        assert "aircraft" in params
        assert "altitude_ranges" in params
        assert "squawks" in params
        assert "categories" in params
        assert "data_sources" in params
        assert "airspaces" in params
        assert "gspeed" in params
        assert "limit" in params
