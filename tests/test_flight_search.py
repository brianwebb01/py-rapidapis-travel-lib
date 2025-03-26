import pytest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime
from skyscanner_travel.services.flight_search import FlightSearch
from skyscanner_travel.models.flight import Flight
from skyscanner_travel.models.flight_response import FlightSearchResponse
from skyscanner_travel.services.skyscanner_client import SkyscannerClient

@pytest.fixture
def mock_response_data():
    with open('tests/stubs/flight_search_response.json', 'r') as f:
        return json.load(f)

@pytest.fixture
def flight_search():
    return FlightSearch(api_key="test_api_key")

@pytest.fixture
def mock_api_response():
    with patch('skyscanner_travel.services.skyscanner_client.SkyscannerClient._make_request') as mock_request:
        mock_request.return_value = {
            "flights": [
                {
                    "id": "FL123",
                    "origin": "DFW",
                    "origin_city": "Dallas",
                    "destination": "LAX",
                    "destination_city": "Los Angeles",
                    "departure": {
                        "date": "04/01/2024",
                        "time": "10:00 AM"
                    },
                    "arrival": {
                        "date": "04/01/2024",
                        "time": "12:00 PM"
                    },
                    "airline": "American Airlines",
                    "flight_number": "AA123",
                    "cabin_class": "ECONOMY",
                    "stops": [],
                    "total_duration": "2h",
                    "itinerary_id": "IT123",
                    "price": {
                        "amount": 199.99,
                        "currency": "USD"
                    }
                }
            ],
            "total_results": 1,
            "currency": "USD",
            "market": "US",
            "locale": "en-US",
            "country_code": "US"
        }
        yield mock_request

def test_basic_flight_search(mock_api_response):
    flight_search = FlightSearch(api_key="test_api_key")
    response = flight_search.search("DFW", "LAX", "2024-04-01")
    assert len(response.flights) == 1
    assert response.total_results == 1

def test_flight_search_with_all_options(mock_api_response):
    flight_search = FlightSearch(api_key="test_api_key")
    response = flight_search.search(
        origin="DFW",
        destination="LAX",
        date="2024-04-01",
        cabin_class="BUSINESS",
        adults=2,
        children=1,
        infants=1,
        currency="EUR",
        market="UK",
        locale="en-GB",
        country_code="GB"
    )
    assert len(response.flights) == 1
    assert response.total_results == 1

def test_flight_search_with_existing_suffixes(mock_api_response):
    flight_search = FlightSearch(api_key="test_api_key")
    response = flight_search.search("DFW", "LAX", "2024-04-01")
    assert len(response.flights) == 1
    assert response.total_results == 1

def test_flight_model_structure(mock_api_response):
    flight_search = FlightSearch(api_key="test_api_key")
    response = flight_search.search("DFW", "LAX", "2024-04-01")
    flight = response.flights[0]
    assert flight.id == "FL123"
    assert flight.origin.id == "DFW"
    assert flight.destination.id == "LAX"
    assert flight.departure == "2024-04-01T10:00:00"
    assert flight.arrival == "2024-04-01T12:00:00"
    assert flight.total_duration == "2h"
    assert flight.stops == 0
    assert flight.price.amount == 199.99
    assert flight.price.currency == "USD"

def test_stop_model_structure(mock_api_response):
    flight_search = FlightSearch(api_key="test_api_key")
    response = flight_search.search("DFW", "LAX", "2024-04-01")
    flight = response.flights[0]
    assert flight.stops == 0

def test_response_methods(mock_api_response):
    flight_search = FlightSearch(api_key="test_api_key")
    response = flight_search.search("DFW", "LAX", "2024-04-01")
    assert str(response) == "1 flights found"

def test_error_handling(mock_api_response):
    flight_search = FlightSearch(api_key="test_api_key")
    with pytest.raises(Exception) as exc_info:
        flight_search.search("INVALID", "INVALID", "2024-04-01")
    assert str(exc_info.value) == "API request failed: HTTP Error"