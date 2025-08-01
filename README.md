# Flightradar24 Python SDK

Official Python SDK for the [Flightradar24 API](https://fr24api.flightradar24.com).

## Features

- Access to all Flightradar24 API v1 endpoints.
- Intuitive client interface: `client.airports.get_full("WAW")`
- Typed responses.
- Robust error handling with custom exceptions.
- Synchronous client (async coming soon).
- Lightweight input validation for common parameters.

## Installation

### Release Version
**Using uv:**
```bash
uv pip install fr24sdk
```

**Using pip:**
```bash
pip install fr24sdk
```

## SDK Usage Guide

This guide provides a comprehensive overview of how to use the `fr24sdk` to interact with the Flightradar24 API.

### 1. Client Initialization

The `Client` is your main entry point to the API.

**Using Environment Variable:**

Ensure your API token is set as an environment variable `FR24_API_TOKEN`.
```bash
export FR24_API_TOKEN="your_actual_token_here" # On Linux/macOS
# set FR24_API_TOKEN=your_actual_token_here # On Windows Command Prompt
# $Env:FR24_API_TOKEN="your_actual_token_here" # On Windows PowerShell
```

Then, initialize the client:
```python
from fr24sdk.client import Client

client = Client()
```

**Passing Token Directly:**
You can also pass the API token directly during client initialization.
```python
client = Client(api_token="your_actual_token_here")
```

**Using as a Context Manager:**
This ensures the underlying HTTP client is closed properly.
```python
from fr24sdk.client import Client

with Client() as client:
    client.flight_summary(flight_ids="")
    pass
```

### 2. Accessing API Resources

The client provides access to different API resources as attributes. For example:

- `client.airlines`: Fetch airline details.
- `client.airports`: Fetch airport details.
- `client.live`: Get live flight data, including flights within specific geographical bounds.
- `client.historic`: Query historic flight information.
- `client.flight_summary`: Retrieve summaries for specific flights.
- `client.flight_tracks`: Access flight track data.
- `client.usage`: Check your API usage statistics.

Each resource object then has methods to fetch data related to that resource.

### 3. Resource Examples

The SDK provides intuitive access to various API resources. Here's how you can typically interact with them:

**a. Fetching Airport Details**

This example demonstrates fetching detailed information for an airport (e.g., Warsaw Chopin Airport - WAW) and accessing its attributes.

```python
from fr24sdk.client import Client
from fr24sdk.exceptions import ApiError

# Initialize client (ensure FR24_API_TOKEN is set or pass api_token="your_token")
client = Client()

airport_iata = "WAW"
print(f"Fetching full details for airport: {airport_iata}")

airport_details = client.airports.get_full(airport_iata)

if airport_details:
    print(f"  Name: {airport_details.name}")
    print(f"  ICAO: {airport_details.icao}")
    print(f"  City: {airport_details.city}")
    print(f"  Country: {airport_details.country_name}")
    print(f"  Latitude: {airport_details.lat}")
    print(f"  Longitude: {airport_details.lon}")
```

**b. Other Available Resources**

The client provides access to a comprehensive set of Flightradar24 API resources, including but not limited to:

-   `client.airlines`: Fetch airline details.
-   `client.live`: Get live flight data, including flights within specific geographical bounds.
-   `client.flight_summary`: Retrieve summaries for specific flights.
-   `client.flight_tracks`: Access flight track data.
-   `client.historic`: Query historic flight information.
-   `client.usage`: Check your API usage statistics.

Each of these resources offers methods to interact with the corresponding API endpoints. For example, you might use `client.live.get_flights(...)` or `client.airlines.get_by_iata(...)`. Please refer to the SDK's source code or future detailed documentation for specific method signatures and parameters.

### 4. Handling Responses

API methods return Python objects that represent the JSON response from the API. You can access data using dot notation, as shown in the examples.

```python
# Example with AirportFull object
# waw_full = client.airports.get_full("WAW")
# print(waw_full.name)
# print(waw_full.timezone_name)
```

### 5. Error Handling

The SDK uses custom exceptions to indicate errors. The base exception is `Fr24SdkError`. More specific errors like `ApiError`, `AuthenticationError`, `RateLimitError`, etc., inherit from it.

```python
import os
from fr24sdk.client import Client
from fr24sdk.exceptions import ApiError, AuthenticationError, Fr24SdkError # Import relevant exceptions

# Assumes FR24_API_TOKEN is set, or pass it to Client()
try:
    with Client() as client:
        # Example: Intentionally try to get a non-existent airport
        airport = client.airports.get_full("INVALID_IATA")
        if airport:
            print(airport.name)

except AuthenticationError:
    print("Authentication failed. Please check your API token.")
except ApiError as e:
    print(f"API Error occurred: Status {e.status}, Message: {e.message}")
    print(f"Request URL: {e.request_url}")
    if e.body:
        print(f"Response body: {e.body}")
except Fr24SdkError as e:
    print(f"An SDK-specific error occurred: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

### 6. Closing the Client

If you are not using the client as a context manager (`with Client() as client:`), you should explicitly close it to release resources:

```python
client = Client()
# ... use client ...
client.close()
```

## Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for guidelines.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details. 
