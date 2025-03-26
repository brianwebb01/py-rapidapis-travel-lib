import requests
import json
from typing import Dict, List, Optional, Any
from ..models.flight import Flight
from ..models.flight_response import FlightSearchResponse
from ..models.location import Location
from ..models.location_response import LocationResponse

class SkyscannerClient:
    """Client for interacting with the Skyscanner API via RapidAPI."""

    def __init__(self, api_key: str):
        """Initialize the client with an API key.

        Args:
            api_key (str): RapidAPI key for Skyscanner API
        """
        if not api_key:
            raise ValueError("API key cannot be empty")
        self.api_key = api_key
        self.api_host = "sky-scrapper.p.rapidapi.com"
        self.base_url = f"https://{self.api_host}/api"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host
        }

    def _make_request(self, endpoint: str, method: str = "GET", params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to the Skyscanner API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data
            )
            if response.status_code == 403:
                print(f"Request details:")
                print(f"URL: {url}")
                print(f"Headers: {self.headers}")
                print(f"Params: {params}")
                raise requests.exceptions.RequestException("API key is invalid or expired. Please check your RapidAPI key.")
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.HTTPError, requests.exceptions.RequestException) as e:
            raise requests.exceptions.RequestException(f"API request failed: {str(e)}")
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid JSON response: {str(e)}")

    def search_locations(self, query: str, locale: str = "en-US") -> Dict[str, Any]:
        """Search for locations (airports, cities) by query string.

        Args:
            query (str): Search query (e.g. airport code or city name)
            locale (str): Locale code (default: en-US)

        Returns:
            Dict: API response containing location results
        """
        endpoint = "v1/flights/searchAirport"
        params = {"query": query, "locale": locale}
        try:
            response = self._make_request(endpoint, params=params)
            if isinstance(response, dict):
                if 'data' in response:
                    # Convert the new format to our standard format
                    locations = []
                    for item in response['data']:
                        location = {
                            'id': item.get('entityId', ''),
                            'code': item.get('skyId', ''),
                            'name': item.get('presentation', {}).get('title', ''),
                            'type': item.get('navigation', {}).get('entityType', ''),
                            'city_name': item.get('presentation', {}).get('title', ''),
                            'region_name': '',  # Not available in v1 response
                            'country_name': item.get('presentation', {}).get('subtitle', ''),
                            'distance_to_city_value': None,  # Not available in v1 response
                            'distance_to_city_unit': None   # Not available in v1 response
                        }
                        locations.append(location)
                    return {'data': locations}
                elif 'places' in response:
                    # Convert places format to locations format
                    locations = []
                    for place in response['places']:
                        distance = place.get('distanceToCity', {}) or {}
                        location = {
                            'id': place.get('entityId', ''),
                            'code': place.get('entityId', '').split('.')[0] if '.' in place.get('entityId', '') else place.get('entityId', ''),
                            'name': place.get('name', ''),
                            'type': place.get('type', ''),
                            'city_name': place.get('city', {}).get('name', '') or place.get('name', ''),
                            'region_name': place.get('region', {}).get('name', ''),
                            'country_name': place.get('country', {}).get('name', ''),
                            'distance_to_city_value': distance.get('value'),
                            'distance_to_city_unit': distance.get('unit')
                        }
                        locations.append(location)
                    return {'data': locations}
                else:
                    # Create a standard format if neither exists
                    distance = response.get('distanceToCity', {}) or {}
                    return {
                        'data': [
                            {
                                'id': response.get('entityId', ''),
                                'code': response.get('entityId', '').split('.')[0] if '.' in response.get('entityId', '') else response.get('entityId', ''),
                                'name': response.get('name', ''),
                                'type': response.get('type', ''),
                                'city_name': response.get('city', {}).get('name', '') or response.get('name', ''),
                                'region_name': response.get('region', {}).get('name', ''),
                                'country_name': response.get('country', {}).get('name', ''),
                                'distance_to_city_value': distance.get('value'),
                                'distance_to_city_unit': distance.get('unit')
                            }
                        ]
                    }
            return response
        except requests.exceptions.RequestException as e:
            raise

    def search_flights(
        self,
        origin_sky_id: str,
        destination_sky_id: str,
        origin_entity_id: str,
        destination_entity_id: str,
        date: str,
        cabin_class: str = "economy",
        adults: int = 1,
        children: int = 0,
        infants: int = 0,
        currency: str = "USD",
        market: str = "en-US",
        country_code: str = "US"
    ) -> Dict:
        """Search for available flights.

        Args:
            origin_sky_id (str): Origin airport Sky ID (e.g. "SDF")
            destination_sky_id (str): Destination airport Sky ID (e.g. "LAS")
            origin_entity_id (str): Origin airport entity ID
            destination_entity_id (str): Destination airport entity ID
            date (str): Departure date in YYYY-MM-DD format
            cabin_class (str): Cabin class (default: economy)
            adults (int): Number of adult passengers
            children (int): Number of child passengers
            infants (int): Number of infant passengers
            currency (str): Currency code (default: USD)
            market (str): Market code (default: en-US)
            country_code (str): Country code (default: US)

        Returns:
            Dict: API response containing flight results
        """
        params = {
            "originSkyId": origin_sky_id,
            "destinationSkyId": destination_sky_id,
            "originEntityId": origin_entity_id,
            "destinationEntityId": destination_entity_id,
            "date": date,
            "cabinClass": cabin_class,
            "adults": str(adults),
            "childrens": str(children),
            "infants": str(infants),
            "currency": currency,
            "market": market,
            "countryCode": country_code
        }
        return self._make_request("v2/flights/searchFlights", params=params)

    def get_flight_details(self, itinerary_id: str, session_id: str) -> Flight:
        """Get detailed information about a specific flight.

        Args:
            itinerary_id (str): Itinerary ID from flight search
            session_id (str): Session ID from flight search

        Returns:
            Flight: Detailed flight information
        """
        endpoint = f"v3/flights/details/{itinerary_id}"
        params = {"session_id": session_id}
        response = self._make_request(endpoint, params=params)
        return Flight.from_api_response(response)