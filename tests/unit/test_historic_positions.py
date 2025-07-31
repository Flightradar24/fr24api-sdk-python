# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Unit tests for the historic_positions module."""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timezone

from fr24sdk.resources.historic.positions import (
    HistoricPositionsResource,
    _HistoricPositionsParams,
    MIN_HISTORIC_DATETIME,
)
from fr24sdk.models.flight import (
    FlightPositionsLightResponse,
    FlightPositionsFullResponse,
    CountResponse,
)
from fr24sdk.transport import HttpTransport


class TestHistoricPositionsParams:
    """Test the _HistoricPositionsParams class."""

    def test_validate_timestamp_datetime(self):
        """Test timestamp validation with datetime objects."""
        # Valid datetime (with timezone)
        valid_dt = datetime(2020, 1, 1, tzinfo=timezone.utc)
        params = _HistoricPositionsParams(timestamp=valid_dt)
        assert isinstance(params.timestamp, int)
        assert params.timestamp == int(valid_dt.timestamp())

        # Valid datetime (without timezone - should be converted to UTC)
        valid_dt_no_tz = datetime(2020, 1, 1)
        params = _HistoricPositionsParams(timestamp=valid_dt_no_tz)
        assert isinstance(params.timestamp, int)
        assert params.timestamp == int(
            valid_dt_no_tz.replace(tzinfo=timezone.utc).timestamp()
        )

    def test_validate_timestamp_integer(self):
        """Test timestamp validation with integer values."""
        # Valid timestamp
        valid_ts = int(datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp())
        params = _HistoricPositionsParams(timestamp=valid_ts)
        assert params.timestamp == valid_ts

    def test_timestamp_too_early(self):
        """Test validation fails for timestamps before the minimum allowed date."""
        # Invalid timestamp (before minimum date)
        invalid_dt = datetime(2016, 1, 1, tzinfo=timezone.utc)
        with pytest.raises(Exception) as exc_info:
            _HistoricPositionsParams(timestamp=invalid_dt)
        assert "Timestamp must be after" in str(exc_info.value)

        # Invalid integer timestamp
        invalid_ts = int(MIN_HISTORIC_DATETIME.timestamp()) - 100
        with pytest.raises(Exception) as exc_info:
            _HistoricPositionsParams(timestamp=invalid_ts)
        assert "Timestamp must be after" in str(exc_info.value)

    def test_serialize_params(self):
        """Test parameters are correctly serialized for API requests."""
        # Test with various parameter types
        params = _HistoricPositionsParams(
            timestamp=datetime(2020, 1, 1, tzinfo=timezone.utc),
            bounds="10,20,30,40",
            flights=["AB1234", "CD5678"],
            callsigns=["ABC123"],
            altitude_ranges=["1000,5000", "10000,20000"],
            limit=100,
        )

        serialized = params._to_query_dict()

        # Check serialization results
        assert isinstance(serialized["timestamp"], int)
        assert serialized["bounds"] == "10,20,30,40"
        assert serialized["flights"] == "AB1234,CD5678"
        assert serialized["callsigns"] == "ABC123"
        assert serialized["altitude_ranges"] == "1000,5000,10000,20000"
        assert serialized["limit"] == 100

        # Check that None values are not included
        assert "registrations" not in serialized


class TestHistoricPositionsResource:
    """Test the HistoricPositionsResource class."""

    @pytest.fixture
    def mock_transport(self):
        """Create a mock transport."""
        mock = Mock(spec=HttpTransport)
        return mock

    @pytest.fixture
    def historic_positions(self, mock_transport):
        """Create a HistoricPositionsResource with mock transport."""
        return HistoricPositionsResource(mock_transport)

    def test_get_light_success(self, historic_positions, mock_transport):
        """Test successful get_light call."""

        # Configure mock response to return our fake data
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
        result = historic_positions.get_light(
            timestamp=1672574400,  # 2023-01-01T12:00:00Z
            bounds="10,20,30,40",
            flights=["AB1234"],
        )

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
        assert args[1] == "/api/historic/flight-positions/light"
        assert "timestamp" in kwargs["params"]
        assert kwargs["params"]["timestamp"] == 1672574400

    def test_get_light_empty_response(self, historic_positions, mock_transport):
        """Test get_light with empty response."""
        # Mock empty response
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_transport.request.return_value = mock_response

        # Call method
        result = historic_positions.get_light(
            timestamp=datetime(2023, 1, 1, 12, tzinfo=timezone.utc),
            bounds="10,20,30,40",
        )

        # Verify empty result
        assert isinstance(result, FlightPositionsLightResponse)
        assert len(result.data) == 0

    def test_get_full_success(self, historic_positions, mock_transport):
        """Test successful get_full call."""
        # Mock response data

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
                    "flight": "AB1234",
                    "callsign": "ABC123",
                    "type": "B738",
                    "reg": "G-ABCD",
                    "orig_icao": "EGLL",
                    "dest_icao": "EGCC",
                }
            ]
        }
        mock_transport.request.return_value = mock_response

        # Call the method
        result = historic_positions.get_full(
            timestamp=1672574400,  # 2023-01-01T12:00:00Z
            bounds="10,20,30,40",
            flights=["AB1234"],
        )

        # Verify results
        assert isinstance(result, FlightPositionsFullResponse)
        assert len(result.data) == 1
        assert result.data[0].fr24_id == "123456"
        assert result.data[0].flight == "AB1234"
        assert result.data[0].type == "B738"

        # Verify mock was called correctly
        mock_transport.request.assert_called_once()
        args, kwargs = mock_transport.request.call_args
        assert args[0] == "GET"
        assert args[1] == "/api/historic/flight-positions/full"

    def test_get_full_empty_response(self, historic_positions, mock_transport):
        """Test get_full with empty response."""
        # Mock empty response
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_transport.request.return_value = mock_response

        # Call method
        result = historic_positions.get_full(
            timestamp=datetime(2023, 1, 1, 12, tzinfo=timezone.utc),
            bounds="10,20,30,40",
        )

        # Verify empty result
        assert isinstance(result, FlightPositionsFullResponse)
        assert len(result.data) == 0

    def test_count_success(self, historic_positions, mock_transport):
        """Test successful count call."""
        # Mock response data
        response_data = {"record_count": 42}

        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = response_data
        mock_transport.request.return_value = mock_response

        # Call the method
        result = historic_positions.count(
            timestamp=1672574400,  # 2023-01-01T12:00:00Z
            bounds="10,20,30,40",
        )

        # Verify results
        assert isinstance(result, CountResponse)
        assert result.record_count == 42

        # Verify mock was called correctly
        mock_transport.request.assert_called_once()
        args, kwargs = mock_transport.request.call_args
        assert args[0] == "GET"
        assert args[1] == "/api/historic/flight-positions/count"

    def test_with_all_parameters(self, historic_positions, mock_transport):
        """Test a call with all possible parameters."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_transport.request.return_value = mock_response

        # Call with all parameters
        historic_positions.get_light(
            timestamp=datetime(2023, 1, 1, 12, tzinfo=timezone.utc),
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
            gspeed=500,
            limit=100,
        )

        # Verify parameters were correctly passed
        args, kwargs = mock_transport.request.call_args
        params = kwargs["params"]

        # Check all parameters are included
        assert "timestamp" in params
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
        assert "gspeed" in params
        assert "limit" in params
