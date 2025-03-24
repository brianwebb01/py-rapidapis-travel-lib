# Rapid Booking.com SDK

A Python SDK for interacting with Booking.com APIs through RapidAPI. Currently supports flight searches with plans to expand to hotels and car rentals.

## Installation

```bash
pip install rapid-bookingcom
```

For development or running examples, install in development mode from the source directory:
```bash
pip install -e .
```

## Configuration

Before using the SDK, you need to set up your RapidAPI credentials. Create a `.env` file in your project root with the following variables:

```
RAPID_API_KEY=your_rapidapi_key_here
RAPID_API_HOST=booking-com.p.rapidapi.com
```

## Usage

### Flight Search

```python
from rapid_bookingcom import FlightSearch

# Initialize the search client
search = FlightSearch()

# Search for flights
results = search.search(
    origin="SDF",  # Airport code
    destination="LAS",  # Airport code
    depart_date="2024-04-01",  # Format: YYYY-MM-DD
    return_date="2024-04-05",  # Optional
    cabin_class="ECONOMY",  # Optional, defaults to ECONOMY
    adults="1",  # Optional, defaults to 1
    children="0,17",  # Optional, defaults to 0,17
    sort="BEST",  # Optional, defaults to BEST
    currency_code="USD",  # Optional, defaults to USD
    page_no="1"  # Optional, defaults to 1
)

# Print results
results.print_results()

# Save results to JSON
results.save_to_json()
```

### Location Search

```python
from rapid_bookingcom import LocationSearch

# Initialize the search client
search = LocationSearch()

# Search for locations
results = search.search(
    query="New York",  # City name or partial name
    locale="en_US"  # Optional, defaults to en_US
)

# Print results
results.print_results()

# Save results to JSON
results.save_to_json()
```

### Command Line Interface

You can also use the SDK directly from the command line:

```bash
rapid-bookingcom
```

### Examples

The package includes example scripts in the `examples` directory. You can find them in your Python environment after installation:

```bash
python -c "import rapid_bookingcom; print(rapid_bookingcom.__file__)"
```

Navigate to the `examples` directory in the package location to find example scripts like `flight_search.py` and `location_search.py`.

To run an example script, you can use one of these methods:

1. From any directory, using the Python module path:
```bash
python -m rapid_bookingcom.examples.flight_search
python -m rapid_bookingcom.examples.location_search
```

2. From the project root directory (where setup.py is located):
```bash
# First, make sure you're in the project root directory (where setup.py is)
cd /path/to/py-rapidapis-booking-com-lib

# Install the package in development mode
pip install -e .

# Then run the example
python -m rapid_bookingcom.examples.flight_search
python -m rapid_bookingcom.examples.location_search
```

The first method is recommended as it works regardless of your current directory. Make sure you have:
1. Installed the package in development mode (`pip install -e .`)
2. Set up your `.env` file with your RapidAPI credentials

## Features

- Flight search with detailed information
- Support for one-way, round-trip, and multi-city flights
- Detailed stop information for connecting flights
- Price information with currency
- Cabin class selection
- Passenger configuration
- Results can be printed to console or saved to JSON

## Future Features

- Hotel search and booking
- Car rental search and booking
- More booking options and configurations
- Additional API endpoints support

## Requirements

- Python 3.8 or higher
- RapidAPI account with Booking.com API access
- Required Python packages (installed automatically):
  - requests
  - python-dotenv
  - pydantic

## License

MIT License