import pytest
from unittest.mock import patch, MagicMock
import json
import os
from datetime import datetime
from skyscanner_travel.services.flight_search import FlightSearch, FlightSearchError
from skyscanner_travel.models.flight import Flight
from skyscanner_travel.models.flight_response import FlightSearchResponse
from skyscanner_travel.services.skyscanner_client import SkyscannerClient

@pytest.fixture
def mock_response_data():
    with open('tests/stubs/skyscanner_flight_search.json', 'r') as f:
        return json.load(f)

@pytest.fixture
def mock_client(mock_response_data):
    client = MagicMock()
    client.search_flights.return_value = mock_response_data
    return client

@pytest.fixture
def flight_search(mock_client):
    return FlightSearch(mock_client)

def test_basic_flight_search(flight_search):
    response = flight_search.search(
        origin_sky_id="SDF",
        destination_sky_id="LAS",
        origin_entity_id="95673969",
        destination_entity_id="95673753",
        date="2025-03-30"
    )
    assert len(response.flights) > 0
    assert response.total_results > 0

def test_flight_search_with_all_options(flight_search):
    response = flight_search.search(
        origin_sky_id="SDF",
        destination_sky_id="LAS",
        origin_entity_id="95673969",
        destination_entity_id="95673753",
        date="2025-03-30",
        cabin_class="BUSINESS",
        adults=2,
        children=1,
        infants=1,
        currency="EUR",
        market="UK",
        country_code="GB"
    )
    assert len(response.flights) > 0
    assert response.total_results > 0

def test_flight_model_structure(flight_search):
    response = flight_search.search(
        origin_sky_id="SDF",
        destination_sky_id="LAS",
        origin_entity_id="95673969",
        destination_entity_id="95673753",
        date="2025-03-30"
    )
    flight = response.flights[0]
    assert flight.id is not None
    assert flight.origin.code == "SDF"
    assert flight.destination.code == "LAS"
    assert isinstance(flight.departure, dict)
    assert isinstance(flight.arrival, dict)
    assert flight.total_duration is not None
    assert isinstance(flight.stops, (list, int))
    assert flight.price.amount > 0
    assert flight.price.currency == "USD"
    assert flight.session_id is not None

def test_stop_model_structure(flight_search):
    response = flight_search.search(
        origin_sky_id="SDF",
        destination_sky_id="LAS",
        origin_entity_id="95673969",
        destination_entity_id="95673753",
        date="2025-03-30"
    )
    flight = response.flights[0]
    if isinstance(flight.stops, list):
        for stop in flight.stops:
            assert stop.airport is not None
            assert stop.city is not None
            assert stop.duration is not None

def test_response_methods(flight_search):
    response = flight_search.search(
        origin_sky_id="SDF",
        destination_sky_id="LAS",
        origin_entity_id="95673969",
        destination_entity_id="95673753",
        date="2025-03-30"
    )
    assert str(response) == f"Found {response.total_results} flights"

def test_error_handling(flight_search):
    flight_search.client.search_flights.side_effect = Exception("API request failed")
    with pytest.raises(Exception) as exc_info:
        flight_search.search(
            origin_sky_id="INVALID",
            destination_sky_id="INVALID",
            origin_entity_id="invalid",
            destination_entity_id="invalid",
            date="2025-03-30"
        )
    assert "Failed to search flights" in str(exc_info.value)