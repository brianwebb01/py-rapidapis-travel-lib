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

        response = self.client._make_request(self.endpoint, params=querystring)

        if isinstance(response, dict):
            if not response.get('status', True):
                raise LocationSearchError(response.get('message', 'Unknown error occurred'))
            data = response.get('data', [])
        else:
            data = response

        locations = [Location(**location) for location in data]
        return LocationSearchResponse(locations)
