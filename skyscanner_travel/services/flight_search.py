from typing import List, Optional, Dict, Any
from datetime import datetime
from .skyscanner_client import SkyscannerClient
from ..models.location import Location
from ..models.flight import Flight, Price, Stop
from ..models.flight_response import FlightSearchResponse

class FlightSearchError(Exception):
    pass

class FlightSearch:
    """Service for searching flights using the Skyscanner API."""

    def __init__(self, client: SkyscannerClient):
        """Initialize the service with a client.

        Args:
            client (SkyscannerClient): Initialized SkyscannerClient instance
        """
        self.client = client

    def search_locations(self, query: str) -> List[Location]:
        """Search for locations (airports, cities) by query string.

        Args:
            query (str): Search query (e.g. airport code or city name)

        Returns:
            List[Location]: List of matching locations
        """
        response = self.client.search_locations(query)
        if not response.get('status'):
            raise ValueError("API request failed")

        return [
            Location.from_api_response(item)
            for item in response.get('data', [])
            if item.get('navigation', {}).get('entityType') == 'AIRPORT'
        ]

    def search(
        self,
        origin_sky_id: str,
        destination_sky_id: str,
        origin_entity_id: str,
        destination_entity_id: str,
        date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        children: int = 0,
        infants: int = 0,
        cabin_class: str = "economy",
        currency: str = "USD",
        market: str = "en-US",
        country_code: str = "US"
    ) -> FlightSearchResponse:
        """Search for available flights.

        Args:
            origin_sky_id (str): Origin airport Sky ID (e.g. "SDF")
            destination_sky_id (str): Destination airport Sky ID (e.g. "LAS")
            origin_entity_id (str): Origin airport entity ID
            destination_entity_id (str): Destination airport entity ID
            date (str): Departure date in YYYY-MM-DD format
            return_date (Optional[str]): Return date in YYYY-MM-DD format (not supported in v2 API)
            adults (int): Number of adult passengers
            children (int): Number of child passengers
            infants (int): Number of infant passengers
            cabin_class (str): Cabin class (default: economy)
            currency (str): Currency code (default: USD)
            market (str): Market code (default: en-US)
            country_code (str): Country code (default: US)

        Returns:
            FlightSearchResponse: Response containing flight results
        """
        try:
            # Make the API request
            response = self.client.search_flights(
                origin_sky_id=origin_sky_id,
                destination_sky_id=destination_sky_id,
                origin_entity_id=origin_entity_id,
                destination_entity_id=destination_entity_id,
                date=date,
                cabin_class=cabin_class,
                adults=adults,
                children=children,
                infants=infants,
                currency=currency,
                market=market,
                country_code=country_code
            )

            # Validate response format
            if not isinstance(response, dict) or 'data' not in response:
                raise Exception("API request failed: Invalid response format")

            data = response['data']
            if not isinstance(data, dict) or 'itineraries' not in data:
                raise Exception("API request failed: Invalid response format")

            # Process flights using Flight.from_api_response
            flights = []
            for itinerary in data.get('itineraries', []):
                # Pass the full response structure to maintain the session ID at root level
                flight = Flight.from_api_response({
                    "sessionId": response["sessionId"],  # Get session ID from root of original response
                    "data": {
                        "itineraries": [itinerary]
                    }
                })
                flights.append(flight)

            return FlightSearchResponse(
                flights=flights,
                total_results=len(flights),
                currency=currency,
                market=market,
                locale="en-US",  # Default locale
                country_code=country_code
            )

        except Exception as e:
            raise FlightSearchError(f"Failed to search flights: {str(e)}")

    def get_flight_details(self, flight: Flight) -> Flight:
        """Get detailed information about a specific flight.

        Args:
            flight (Flight): Flight object to get details for

        Returns:
            Flight: Detailed flight information

        Raises:
            FlightSearchError: If the API request fails
        """
        response = self.client.get_flight_details(
            flight=flight
        )

        if not response.get('status'):
            error_message = response.get('message', 'Unknown error occurred')
            raise FlightSearchError(f"Failed to get flight details: {error_message}")

        return Flight.from_api_detail_response(response)