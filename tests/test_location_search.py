import json
import os
from unittest.mock import patch, Mock
import pytest
from io import StringIO
import sys
from skyscanner_travel.services.location_search import LocationSearch, LocationSearchError
from skyscanner_travel.models.location import Location
from skyscanner_travel.models.location_response import LocationResponse
from skyscanner_travel.services.flight_search import FlightSearch

def load_stub_data():
    stub_path = os.path.join(os.path.dirname(__file__), "stubs", "location_search_response.json")
    with open(stub_path, "r") as f:
        return json.load(f)

@pytest.fixture
def mock_api_response():
    with patch('skyscanner_travel.services.skyscanner_client.SkyscannerClient._make_request') as mock_request:
        mock_request.return_value = {
            'places': [{
                'entityId': 'DFW.CITY',
                'name': 'Dallas',
                'type': 'CITY',
                'city': {'name': 'Dallas'},
                'region': {'name': 'Texas'},
                'country': {'name': 'United States'},
                'distanceToCity': None
            }]
        }
        yield mock_request

@pytest.fixture
def mock_api_error():
    with patch('skyscanner_travel.services.skyscanner_client.SkyscannerClient._make_request') as mock_request:
        mock_request.side_effect = Exception("API request failed: HTTP Error")
        yield mock_request

@pytest.fixture
def mock_location_data():
    return {
        "id": "DFW.AIRPORT",
        "type": "AIRPORT",
        "name": "Dallas Fort Worth International",
        "city_name": "Dallas",
        "country_name": "United States",
        "distance": 25.5,
        "parent": "DFW"
    }

@pytest.fixture
def city_data():
    return {
        "id": "DFW.CITY",
        "type": "CITY",
        "name": "Dallas",
        "country_name": "United States"
    }

@pytest.fixture
def airport_data():
    return {
        "id": "DAL.AIRPORT",
        "type": "AIRPORT",
        "name": "Dallas Love Field",
        "city_name": "Dallas"
    }

@pytest.fixture
def location_search():
    return LocationSearch(api_key="test_api_key")

def test_location_model_structure(mock_api_response):
    location_search = LocationSearch(api_key="test_api_key")
    response = location_search.search("Dallas")
    location = response.locations[0]
    assert location.entity_id == "DFW.CITY"
    assert location.type == "CITY"
    assert location.name == "Dallas"
    assert location.city_name == "Dallas"
    assert location.country_name == "United States"
    assert location.region_name == "Texas"
    assert location.code == "DFW"

def test_location_search_success(mock_api_response):
    location_search = LocationSearch(api_key="test_api_key")
    response = location_search.search("Dallas")
    assert isinstance(response, LocationResponse)
    assert len(response.locations) == 1
    location = response.locations[0]
    assert location.entity_id == "DFW.CITY"
    assert location.type == "CITY"

def test_location_search_error(mock_api_error):
    location_search = LocationSearch(api_key="test_api_key")
    with pytest.raises(LocationSearchError) as exc_info:
        location_search.search("Invalid")
    assert str(exc_info.value) == "API request failed: HTTP Error"

def test_location_search_response_printing(mock_api_response):
    location_search = LocationSearch(api_key="test_api_key")
    response = location_search.search("Dallas")

    # Capture stdout
    captured_output = StringIO()
    sys.stdout = captured_output

    response.print_results()

    # Restore stdout
    sys.stdout = sys.__stdout__

    expected_output = """
Found 1 locations:

1. Dallas
   Code: DFW
   Type: CITY
   Entity ID: DFW.CITY
   Country: United States
   Region: Texas

--------------------------------------------------
"""
    assert captured_output.getvalue() == expected_output

def test_location_search_response_printing_city(mock_api_response):
    location_search = LocationSearch(api_key="test_api_key")
    response = location_search.search("Dallas")

    # Mock print function
    with patch('builtins.print') as mock_print:
        response.print_results()
        mock_print.assert_any_call("Dallas")
        mock_print.assert_any_call("Code: DFW")
        mock_print.assert_any_call("Type: CITY")
        mock_print.assert_any_call("Entity ID: DFW.CITY")
        mock_print.assert_any_call("Country: United States")
        mock_print.assert_any_call("Region: Texas")

def test_location_search_response_printing_airport_no_distance(mock_api_response):
    mock_api_response.return_value = {
        'places': [{
            'entityId': 'DFW.AIRPORT',
            'name': 'Dallas Fort Worth International',
            'type': 'AIRPORT',
            'city': {'name': 'Dallas'},
            'region': {'name': 'Texas'},
            'country': {'name': 'United States'},
            'distanceToCity': None
        }]
    }
    location_search = LocationSearch(api_key="test_api_key")
    response = location_search.search("Dallas")

    # Mock print function
    with patch('builtins.print') as mock_print:
        response.print_results()
        mock_print.assert_any_call("Dallas Fort Worth International")
        mock_print.assert_any_call("Code: DFW")
        mock_print.assert_any_call("Type: AIRPORT")
        mock_print.assert_any_call("Entity ID: DFW.AIRPORT")
        mock_print.assert_any_call("Country: United States")
        mock_print.assert_any_call("Region: Texas")