from ..models.location import Location
from ..models.location_response import LocationSearchResponse
from .client import BookingAPIClient
import json

class LocationSearchError(Exception):
    pass

class LocationSearch:
    def __init__(self):
        self.client = BookingAPIClient()
        self.endpoint = "/flights/searchDestination"

    def search(self, query: str):
        """
        Search for locations based on a query.

        Args:
            query (str): The search query.

        Returns:
            LocationSearchResponse: The response containing a list of locations.

        Raises:
            LocationSearchError: If the API returns an error response.
        """
        querystring = {
            "query": query
        }

        data = self.client._make_request(self.endpoint, params=querystring)

        if isinstance(data, dict) and not data.get('status', True):
            raise LocationSearchError(data.get('message', 'Unknown error occurred'))

        locations = [Location(**location) for location in data]
        return LocationSearchResponse(locations)
