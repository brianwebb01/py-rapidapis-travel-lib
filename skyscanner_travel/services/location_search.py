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
        """
        response = self.client.search_locations(query)
        return LocationResponse.from_api_response(response)

    def print_results(self, response: LocationResponse) -> None:
        """Print the search results in a formatted way."""
        print(f"\nFound {response.total_results} locations:")
        for i, location in enumerate(response.locations, 1):
            print(f"\n{i}. {location}")
            print(f"   Entity ID: {location.entity_id}")
            if location.type == "AIRPORT" and location.city_name:
                print(f"   City: {location.city_name}")
            print(f"   Country: {location.country_name}")
