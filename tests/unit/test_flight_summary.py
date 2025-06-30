# SPDX-FileCopyrightText: Copyright Flightradar24
#
# SPDX-License-Identifier: MIT
"""Unit tests for the flight_summary module."""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timezone

from fr24sdk.resources.flight_summary import FlightSummaryResource, _FlightSummaryParams
from fr24sdk.models.flight import (
    FlightSummaryLightResponse,
    FlightSummaryFullResponse,
    CountResponse,
)
from fr24sdk.transport import HttpTransport


class TestFlightSummaryParams:
    """Test the _FlightSummaryParams class."""

    def test_serialize_params(self):
        """Test parameters are correctly serialized for API requests."""
        # Test with various parameter types
        test_datetime = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        params = _FlightSummaryParams(
            flight_datetime_from=test_datetime,
            flight_datetime_to=test_datetime,
            flights=["BA1234", "LH5678"],
            callsigns=["BAW123"],
            aircraft=["B738", "A320"],
        )

        serialized = params._to_query_dict()

        # Check serialization results
        assert serialized["flight_datetime_from"] == str(test_datetime)
        assert serialized["flight_datetime_to"] == str(test_datetime)
        assert serialized["flights"] == "BA1234,LH5678"
        assert serialized["callsigns"] == "BAW123"
        assert serialized["aircraft"] == "B738,A320"

        # Check that None values are not included
        assert "registrations" not in serialized


class TestFlightSummaryResource:
    """Test the FlightSummaryResource class."""

    @pytest.fixture
    def mock_transport(self):
        """Create a mock transport."""
        mock = Mock(spec=HttpTransport)
        return mock

    @pytest.fixture
    def flight_summary(self, mock_transport):
        """Create a FlightSummaryResource with mock transport."""
        return FlightSummaryResource(mock_transport)

    def test_get_light_success_with_flight_ids(self, flight_summary, mock_transport):
        """Test successful get_light call with flight_ids."""
        # Mock response data
        response_data = {
            "data": [
                {
                    "fr24_id": "35f2ffd9",
                    "flight": "BA1234",
                    "callsign": "BAW123",
                    "operating_as": "BAW",
                    "painted_as": "BAW",
                    "type": "B738",
                    "reg": "G-ABCD",
                    "orig_icao": "EGLL",
                    "datetime_takeoff": "2023-01-01T10:00:00Z",
                    "dest_icao": "EGCC",
                    "datetime_landed": "2023-01-01T11:00:00Z",
                    "hex": "40123A",
                    "first_seen": "2023-01-01T09:45:00Z",
                    "last_seen": "2023-01-01T11:15:00Z",
                    "flight_ended": True,
                }
            ]
        }

        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = response_data
        mock_transport.request.return_value = mock_response

        # Call the method
        result = flight_summary.get_light(flight_ids=["35f2ffd9"])

        # Verify results
        assert isinstance(result, FlightSummaryLightResponse)
        assert len(result.data) == 1
        assert result.data[0].fr24_id == "35f2ffd9"
        assert result.data[0].flight == "BA1234"

        # Verify mock was called correctly
        mock_transport.request.assert_called_once()
        args, kwargs = mock_transport.request.call_args
        assert args[0] == "GET"
        assert args[1] == "/api/flight-summary/light"
        assert "flight_ids" in kwargs["params"]
        assert kwargs["params"]["flight_ids"] == "35f2ffd9"

    def test_get_light_success_with_datetime_range(
        self, flight_summary, mock_transport
    ):
        """Test successful get_light call with datetime range."""
        # Mock response data
        response_data = {
            "data": [{"fr24_id": "35f2ffd9", "flight": "BA1234", "callsign": "BAW123"}]
        }

        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = response_data
        mock_transport.request.return_value = mock_response

        # Call with datetime parameters
        from_dt = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        to_dt = datetime(2023, 1, 1, 23, 59, 59, tzinfo=timezone.utc)

        result = flight_summary.get_light(
            flight_datetime_from=from_dt, flight_datetime_to=to_dt, airports=["EGLL"]
        )

        # Verify results
        assert isinstance(result, FlightSummaryLightResponse)

        # Verify parameters were passed correctly
        args, kwargs = mock_transport.request.call_args
        assert "flight_datetime_from" in kwargs["params"]
        assert "flight_datetime_to" in kwargs["params"]
        assert kwargs["params"]["airports"] == "EGLL"

    def test_get_full_success(self, flight_summary, mock_transport):
        """Test successful get_full call."""
        # Mock response data
        response_data = {
            "data": [
                {
                    "fr24_id": "35f2ffd9",
                    "flight": "BA1234",
                    "callsign": "BAW123",
                    "operating_as": "BAW",
                    "painted_as": "BAW",
                    "type": "B738",
                    "reg": "G-ABCD",
                    "orig_icao": "EGLL",
                    "orig_iata": "LHR",
                    "datetime_takeoff": "2023-01-01T10:00:00Z",
                    "runway_takeoff": "27L",
                    "dest_icao": "EGCC",
                    "dest_iata": "MAN",
                    "dest_icao_actual": "EGCC",
                    "dest_iata_actual": "MAN",
                    "datetime_landed": "2023-01-01T11:00:00Z",
                    "runway_landed": "23R",
                    "flight_time": 3600,
                    "actual_distance": 250.5,
                    "circle_distance": 230.0,
                    "hex": "40123A",
                    "first_seen": "2023-01-01T09:45:00Z",
                    "last_seen": "2023-01-01T11:15:00Z",
                    "flight_ended": True,
                }
            ]
        }

        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = response_data
        mock_transport.request.return_value = mock_response

        # Call the method
        result = flight_summary.get_full(flight_ids=["35f2ffd9"])

        # Verify results
        print(result)
        assert isinstance(result, FlightSummaryFullResponse)
        assert len(result.data) == 1
        assert result.data[0].fr24_id == "35f2ffd9"
        assert result.data[0].flight == "BA1234"
        assert result.data[0].runway_takeoff == "27L"
        assert result.data[0].flight_time == 3600

        # Verify mock was called correctly
        mock_transport.request.assert_called_once()
        args, kwargs = mock_transport.request.call_args
        assert args[0] == "GET"
        assert args[1] == "/api/flight-summary/full"

    def test_count_success(self, flight_summary, mock_transport):
        """Test successful count call."""
        # Mock response data
        response_data = {"record_count": 42}

        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = response_data
        mock_transport.request.return_value = mock_response

        # Call the method
        from_dt = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        to_dt = datetime(2023, 1, 1, 23, 59, 59, tzinfo=timezone.utc)

        result = flight_summary.count(
            flight_datetime_from=from_dt, flight_datetime_to=to_dt, airports=["EGLL"]
        )

        # Verify results
        assert isinstance(result, CountResponse)
        assert result.record_count == 42

        # Verify mock was called correctly
        mock_transport.request.assert_called_once()
        args, kwargs = mock_transport.request.call_args
        assert args[0] == "GET"
        assert args[1] == "/api/flight-summary/count"

    def test_with_sort_and_limit(self, flight_summary, mock_transport):
        """Test methods with sort and limit parameters."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_transport.request.return_value = mock_response

        # Call with sort and limit parameters
        flight_summary.get_light(flight_ids=["35f2ffd9"], sort="asc", limit=100)

        # Verify parameters were correctly passed
        args, kwargs = mock_transport.request.call_args
        params = kwargs["params"]
        assert "sort" in params
        assert params["sort"] == "asc"
        assert "limit" in params
        assert params["limit"] == '100'

    def test_with_all_parameters(self, flight_summary, mock_transport):
        """Test a call with all possible parameters."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_transport.request.return_value = mock_response

        # Define test datetime objects
        from_dt = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        to_dt = datetime(2023, 1, 1, 23, 59, 59, tzinfo=timezone.utc)

        # Call with all parameters
        flight_summary.get_light(
            flight_datetime_from=from_dt,
            flight_datetime_to=to_dt,
            flights=["BA1234", "LH5678"],
            callsigns=["BAW123"],
            registrations=["G-ABCD"],
            painted_as=["BAW"],
            operating_as=["BAW"],
            airports=["EGLL"],
            routes=["EGLL-EGCC"],
            aircraft=["B738"],
            sort="asc",
            limit=100,
        )

        # Verify parameters were correctly passed
        args, kwargs = mock_transport.request.call_args
        params = kwargs["params"]

        assert "flight_datetime_from" in params
        assert "flight_datetime_to" in params
        assert "flights" in params
        assert "callsigns" in params
        assert "registrations" in params
        assert "painted_as" in params
        assert "operating_as" in params
        assert "airports" in params
        assert "routes" in params
        assert "aircraft" in params
        assert "sort" in params
        assert "limit" in params
