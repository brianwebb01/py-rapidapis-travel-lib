from typing import List, Dict, Optional
from ..models.location import Location
from ..models.location_response import LocationResponse
from .skyscanner_client import SkyscannerClient

class LocationSearchError(Exception):
    pass

class LocationSearch:
    def __init__(self, api_key: str):
        self.client = SkyscannerClient(api_key)

    def search(self, query: str) -> LocationResponse:
        """Search for locations matching the query.

        Args:
            query (str): Search query

        Returns:
            LocationResponse: Response containing list of locations

        Raises:
            LocationSearchError: If the API request fails
        """
        try:
            response = self.client.search_locations(query)
            if not response or not isinstance(response, dict):
                raise LocationSearchError("Invalid API response format")
            return LocationResponse.from_api_response(response)
        except Exception as e:
            raise LocationSearchError(str(e))

    def print_results(self, response: LocationResponse) -> None:
        """Print the search results in a formatted way."""
        print(f"\nFound {len(response.locations)} locations:")
        for i, location in enumerate(response.locations, 1):
            print(f"\n{i}. {location.name}")
            print(f"   Code: {location.code}")
            print(f"   Type: {location.type}")
            print(f"   Entity ID: {location.entity_id}")
            print(f"   Country: {location.country_name}")
            if location.region_name:
                print(f"   Region: {location.region_name}")
            if location.distance_to_city_value is not None:
                print(f"   Distance to city: {location.distance_to_city_value} {location.distance_to_city_unit}")
        print("\n" + "-" * 50)
