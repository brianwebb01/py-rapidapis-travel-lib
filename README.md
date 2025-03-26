# Skyscanner Travel API Library

A Python library for interacting with the Skyscanner API via RapidAPI to search for flights and get booking URLs.

## Features

- Search for airports and cities
- Search for available flights
- Get detailed flight information
- Generate booking URLs for flights
- Support for different cabin classes
- Support for multi-leg flights with stops

## Installation

```bash
pip install skyscanner-travel
```

## Usage

```python
from skyscanner_travel.services.flight_search import FlightSearch

# Initialize the service with your RapidAPI key
flight_search = FlightSearch(api_key="your-rapidapi-key")

# Search for locations
locations = flight_search.search_locations("LAS")

# Search for flights
flights = flight_search.search_flights(
    origin="SDF",
    destination="LAS",
    date="2025-03-30",
    cabin_class="economy",
    adults=1
)

# Get booking URL for a flight
for flight in flights:
    print(f"Flight {flight.airline} {flight.flight_number}")
    print(f"From: {flight.origin_city} ({flight.origin})")
    print(f"To: {flight.destination_city} ({flight.destination})")
    print(f"Departure: {flight.departure['date']} {flight.departure['time']}")
    print(f"Arrival: {flight.arrival['date']} {flight.arrival['time']}")
    print(f"Price: ${flight.price['amount']} {flight.price['currency']}")
    print(f"Booking URL: {flight.bookingcom_url()}")
    print()
```

## API Reference

### FlightSearch

#### `search_locations(query: str) -> List[Location]`

Search for locations (airports, cities) by query string.

**Parameters:**
- `query` (str): Search query (e.g. airport code or city name)

**Returns:**
- List[Location]: List of matching locations

#### `search_flights(origin: str, destination: str, date: str, cabin_class: str = "economy", adults: int = 1, children: int = 0, infants: int = 0) -> List[Flight]`

Search for available flights.

**Parameters:**
- `origin` (str): Origin airport code (e.g. "SDF")
- `destination` (str): Destination airport code (e.g. "LAS")
- `date` (str): Departure date in YYYY-MM-DD format
- `cabin_class` (str): Cabin class (default: economy)
- `adults` (int): Number of adult passengers
- `children` (int): Number of child passengers
- `infants` (int): Number of infant passengers

**Returns:**
- List[Flight]: List of available flights

### Flight

#### `bookingcom_url() -> str`

Generate a booking URL for the flight.

**Returns:**
- str: The booking URL for the flight

## Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `python -m pytest tests/`

## License

MIT License