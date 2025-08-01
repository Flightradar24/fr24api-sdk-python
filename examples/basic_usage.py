"""Basic usage example for the Flightradar24 SDK.

This script demonstrates how to initialize the client, make a simple API calls.

To run this example:
1. Make sure you have the `fr24sdk` installed.
   - For a release version: `pip install fr24sdk` or `uv pip install fr24sdk`
   - For development: Follow the development setup in README.md.
2. Set your Flightradar24 API token in the `api_token` argument.
3. Run the script: `python examples/basic_usage.py`
"""
import logging
from datetime import datetime, timezone

from fr24sdk.client import Client
from fr24sdk.models.geographic import AltitudeRange, Boundary

# Configure basic logging to see SDK informational messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> None:
    """Demonstrates basic SDK usage."""
    logger.info("Starting Flightradar24 SDK example...")
    with Client() as client:
        print(client.airports.get_light(code="CPH"))
        airport_full = client.airports.get_full(code="CPH")
        if airport_full:
            print(airport_full.lon)
        print(client.airlines.get_light(icao="SAS"))
        flight_summary = client.flight_summary.get_light(flights=["KL1316"], flight_datetime_from=datetime(2025, 5, 13, 12, 0, 0), flight_datetime_to=datetime(2025, 5, 14, 17, 10, 0))
        if flight_summary.data:
            print(flight_summary.data[0].fr24_id)
        print(client.live.flight_positions.get_light(flights=["SK2752"]))
        print(client.live.flight_positions.get_light(bounds=Boundary(north=55.6, south=55.5, west=12.5, east=12.6)))
        print(client.live.flight_positions.get_full(bounds="55.6,55.5,12.5,12.6"))
        historic_light = client.historic.flight_positions.get_light(altitude_ranges=[AltitudeRange(min_altitude=1000, max_altitude=10000), "10000-20000"], timestamp=datetime(2025, 5, 14, 18, 15, 0, tzinfo=timezone.utc))
        if historic_light.data:
            print(historic_light.data[0].fr24_id)
        historic_full = client.historic.flight_positions.get_full(flights=["SK2752"], timestamp=datetime(2025, 5, 14, 18, 15, 0, tzinfo=timezone.utc))
        if historic_full.data:
            print(historic_full.data[0])
        flight_tracks = client.flight_tracks.get(flight_id="3a55c027")
        if flight_tracks.data:
            print(flight_tracks.data[0].fr24_id)

        print(client.historic.flight_events.get_full(flight_ids=["3a55c027"], event_types=["all"]))
        print(client.historic.flight_events.get_light(flight_ids=["3a55c027"], event_types=["all"]))
        print(client.usage.get())

if __name__ == "__main__":
    main()
