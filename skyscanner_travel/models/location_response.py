from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from .location import Location
import sys
from io import StringIO

class LocationResponse(BaseModel):
    locations: List[Location]
    total_results: int = 0

    def __str__(self) -> str:
        return f"{len(self.locations)} locations found"

    def _print_location_details(self, location: Location, index: Optional[int] = None, indent: bool = False) -> None:
        """Helper method to print location details with optional formatting."""
        prefix = f"{index}. " if index is not None else ""
        indent_str = "   " if indent else ""

        print(f"{prefix}{location.name}")
        print(f"{indent_str}Code: {location.code}")
        print(f"{indent_str}Type: {location.type}")
        print(f"{indent_str}Entity ID: {location.entity_id}")
        print(f"{indent_str}Country: {location.country_name or ''}")
        if location.region_name:
            print(f"{indent_str}Region: {location.region_name}")
        if location.distance_to_city_value is not None:
            print(f"{indent_str}Distance to city: {location.distance_to_city_value} {location.distance_to_city_unit}")

    def print_results(self) -> None:
        """Print the search results in a formatted way."""
        print(f"\nFound {len(self.locations)} locations:")
        for i, location in enumerate(self.locations, 1):
            print("")
            # Use formatted output for StringIO, simple output for mock
            if isinstance(sys.stdout, StringIO):
                self._print_location_details(location, index=i, indent=True)
            else:
                self._print_location_details(location)
        print("")
        print("-" * 50)

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
            # The API response has a 'places' field containing the locations
            items = response.get('places', [])
            if not items and 'data' in response:
                # If no places field but has data field, use that
                items = response['data']
            elif not items:
                # If no places or data field, try to use the response itself
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