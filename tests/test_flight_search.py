import pytest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime
from rapid_bookingcom.services.flight_search import FlightSearch
from rapid_bookingcom.models.flight import Flight, Stop
from rapid_bookingcom.models.response import FlightSearchResponse

@pytest.fixture
def flight_search():
    return FlightSearch()

@pytest.fixture
def mock_response_data():
    with open('tests/stubs/flight_search_response.json', 'r') as f:
        return json.load(f)

@pytest.fixture
def mock_api_response(mock_response_data):
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_get.return_value = mock_response
        yield mock_get

def test_basic_flight_search(flight_search, mock_api_response):
    # Test basic search
    response = flight_search.search(
        origin="SDF",
        destination="LAS",
        depart_date="2025-03-30"
    )

    # Verify API call
    mock_api_response.assert_called_once()
    call_args = mock_api_response.call_args[1]
    assert call_args['headers']['x-rapidapi-key'] == flight_search.api_key
    assert call_args['headers']['x-rapidapi-host'] == flight_search.api_host

    # Verify query parameters
    params = call_args['params']
    assert params['fromId'] == 'SDF.AIRPORT'
    assert params['toId'] == 'LAS.AIRPORT'
    assert params['departDate'] == '2025-03-30'
    assert params['returnDate'] is None
    assert params['cabinClass'] == 'ECONOMY'
    assert params['adults'] == '1'
    assert params['children'] == '0,17'
    assert params['sort'] == 'BEST'
    assert params['currency_code'] == 'USD'
    assert params['pageNo'] == '1'

    # Verify response structure
    assert isinstance(response, FlightSearchResponse)
    assert isinstance(response.results, list)
    assert len(response.results) > 0
    assert isinstance(response.results[0], Flight)

def test_flight_search_with_all_options(flight_search, mock_api_response):
    # Test search with all options
    response = flight_search.search(
        origin="SDF",
        destination="LAS",
        depart_date="2025-03-30",
        return_date="2025-04-05",
        cabin_class="BUSINESS",
        adults="2",
        children="0,17,1,12",
        sort="PRICE",
        currency_code="EUR",
        page_no="2"
    )

    # Verify API call
    mock_api_response.assert_called_once()
    call_args = mock_api_response.call_args[1]
    params = call_args['params']
    assert params['fromId'] == 'SDF.AIRPORT'
    assert params['toId'] == 'LAS.AIRPORT'
    assert params['departDate'] == '2025-03-30'
    assert params['returnDate'] == '2025-04-05'
    assert params['cabinClass'] == 'BUSINESS'
    assert params['adults'] == '2'
    assert params['children'] == '0,17,1,12'
    assert params['sort'] == 'PRICE'
    assert params['currency_code'] == 'EUR'
    assert params['pageNo'] == '2'

    # Verify response structure
    assert isinstance(response, FlightSearchResponse)
    assert isinstance(response.results, list)
    assert len(response.results) > 0
    assert isinstance(response.results[0], Flight)

def test_flight_model_structure(flight_search, mock_api_response):
    # Test search
    response = flight_search.search(
        origin="SDF",
        destination="LAS",
        depart_date="2025-03-30"
    )

    # Verify flight model structure
    flight = response.results[0]
    assert isinstance(flight, Flight)
    assert isinstance(flight.origin, str)
    assert isinstance(flight.origin_city, str)
    assert isinstance(flight.destination, str)
    assert isinstance(flight.destination_city, str)
    assert isinstance(flight.departure, dict)
    assert isinstance(flight.arrival, dict)
    assert isinstance(flight.airline, str)
    assert isinstance(flight.flight_number, str)
    assert isinstance(flight.price, dict)
    assert isinstance(flight.cabin_class, str)
    assert isinstance(flight.stops, list)
    assert isinstance(flight.total_duration, str)
    assert isinstance(flight.token, str)
    assert isinstance(flight.trip_type, str)

def test_stop_model_structure(flight_search, mock_api_response):
    # Test search
    response = flight_search.search(
        origin="SDF",
        destination="LAS",
        depart_date="2025-03-30"
    )

    # Find a flight with stops
    flight_with_stops = next((f for f in response.results if f.stops), None)
    if flight_with_stops:
        stop = flight_with_stops.stops[0]
        assert isinstance(stop, Stop)
        assert isinstance(stop.airport, str)
        assert isinstance(stop.city, str)
        assert isinstance(stop.duration, str)

def test_response_methods(flight_search, mock_api_response):
    # Test search
    response = flight_search.search(
        origin="SDF",
        destination="LAS",
        depart_date="2025-03-30"
    )

    # Test print_results method
    assert hasattr(response, 'print_results')
    assert callable(response.print_results)

    # Test save_to_json method
    assert hasattr(response, 'save_to_json')
    assert callable(response.save_to_json)

def test_error_handling(flight_search):
    # Test with invalid response structure
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid": "structure"}
        mock_get.return_value = mock_response

        with pytest.raises(ValueError):
            flight_search.search(
                origin="SDF",
                destination="LAS",
                depart_date="2025-03-30"
            )

    # Test with response missing flight offers
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {}}
        mock_get.return_value = mock_response

        with pytest.raises(ValueError):
            flight_search.search(
                origin="SDF",
                destination="LAS",
                depart_date="2025-03-30"
            )