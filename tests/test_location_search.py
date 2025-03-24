import json
import os
from unittest.mock import patch, MagicMock
import pytest
from rapid_bookingcom.services.location_search import LocationSearch, LocationSearchError
from rapid_bookingcom.models.location import Location
from rapid_bookingcom.models.location_response import LocationSearchResponse

def load_stub_data():
    stub_path = os.path.join(os.path.dirname(__file__), "stubs", "location_search_response.json")
    with open(stub_path, "r") as f:
        return json.load(f)

@pytest.fixture
def mock_api_response():
    return load_stub_data()

@pytest.fixture
def mock_location_data(mock_api_response):
    return mock_api_response['data'][0]

@pytest.fixture
def location_search():
    return LocationSearch()

def test_location_model_structure(mock_location_data):
    """Test that the Location model correctly parses the API response."""
    location = Location(**mock_location_data)

    assert location.id == "DFW.AIRPORT"
    assert location.type == "AIRPORT"
    assert location.name == "Dallas-Fort Worth International Airport"
    assert location.code == "DFW"
    assert location.region_name == "Texas"
    assert location.country_name == "United States"
    assert location.city_name == "Dallas"
    assert location.distance_to_city_value == 25.903681159530844
    assert location.distance_to_city_unit == "km"

def test_location_search_success(location_search, mock_api_response):
    """Test successful location search."""
    with patch.object(location_search.client, '_make_request', return_value=mock_api_response):
        response = location_search.search("Dallas")

        assert isinstance(response, LocationSearchResponse)
        assert len(response.locations) == 1
        location = response.locations[0]

        assert location.id == "DFW.AIRPORT"
        assert location.type == "AIRPORT"
        assert location.name == "Dallas-Fort Worth International Airport"
        assert location.code == "DFW"

def test_location_search_error(location_search):
    """Test location search error handling."""
    error_response = {
        "status": False,
        "message": "API Error"
    }

    with patch.object(location_search.client, '_make_request', return_value=error_response):
        with pytest.raises(LocationSearchError) as exc_info:
            location_search.search("Dallas")

        assert str(exc_info.value) == "API Error"

def test_location_search_response_printing(mock_location_data, capsys):
    """Test the print_results method of LocationSearchResponse."""
    location = Location(**mock_location_data)
    response = LocationSearchResponse([location])

    response.print_results()
    captured = capsys.readouterr()

    expected_output = """
Available Locations:
==================================================

Location 1:
DFW Dallas-Fort Worth International Airport
26 km from downtown
Dallas, Texas, United States
--------------------------------------------------
"""
    assert captured.out == expected_output

def test_location_search_response_printing_city():
    """Test the print_results method for city locations."""
    city_data = {
        "id": "DFW.CITY",
        "type": "CITY",
        "name": "Dallas",
        "code": "DFW",
        "regionName": "Texas",
        "countryName": "United States"
    }
    location = Location(**city_data)
    response = LocationSearchResponse([location])

    with patch('builtins.print') as mock_print:
        response.print_results()

        # Verify the correct format for city locations
        mock_print.assert_any_call("DFW Dallas All Airports")
        mock_print.assert_any_call("Texas, United States")

def test_location_search_response_printing_airport_no_distance():
    """Test the print_results method for airport locations without distance."""
    airport_data = {
        "id": "DAL.AIRPORT",
        "type": "AIRPORT",
        "name": "Dallas Love Field Airport",
        "code": "DAL",
        "regionName": "Texas",
        "countryName": "United States",
        "cityName": "Dallas"
    }
    location = Location(**airport_data)
    response = LocationSearchResponse([location])

    with patch('builtins.print') as mock_print:
        response.print_results()

        # Verify the correct format for airport locations without distance
        mock_print.assert_any_call("DAL Dallas Love Field Airport")
        mock_print.assert_any_call("Dallas, Texas, United States")