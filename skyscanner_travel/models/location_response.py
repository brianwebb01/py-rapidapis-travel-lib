from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from .location import Location

class LocationResponse(BaseModel):
    locations: List[Location]
    total_results: int = 0

    def __str__(self) -> str:
        return f"{len(self.locations)} locations found"

    def print_results(self) -> None:
        """Print the search results in a formatted way."""
        print(f"\nFound {self.total_results} locations:")
        for i, location in enumerate(self.locations, 1):
            print(f"\n{i}. {location.name}")
            print(f"   Code: {location.code}")
            print(f"   Type: {location.type}")
            print(f"   Entity ID: {location.entity_id}")
            if location.city_name:
                print(f"   City: {location.city_name}")
            print(f"   Country: {location.country_name}")
        print("\n" + "-" * 50)

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'LocationResponse':
        """Create a LocationResponse from an API response.

        Args:
            response (Dict[str, Any]): API response containing location data

        Returns:
            LocationResponse: Response containing list of locations
        """
        locations = []
        if isinstance(response, dict):
            # The API response has a 'data' field containing the locations
            items = response.get('data', [])
            if not items:
                # If no data field, try to use the response itself
                items = [response]
        elif isinstance(response, list):
            items = response
        else:
            items = [response]

        for item in items:
            location = Location.from_api_response(item)
            if location:
                locations.append(location)

        return cls(locations=locations, total_results=len(locations))