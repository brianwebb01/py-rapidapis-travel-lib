from typing import List, Optional, Dict, Any
from datetime import datetime
from .skyscanner_client import SkyscannerClient
from ..models.location import Location
from ..models.flight import Flight, FlightSearchResponse, Price, Stop

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

            # Process flights
            flights = []
            for itinerary in data.get('itineraries', []):
                # Get the first leg of the itinerary
                leg = itinerary.get('legs', [{}])[0]

                # Get the first pricing option
                pricing_option = itinerary.get('pricingOptions', [{}])[0]
                price_data = pricing_option.get('price', {})

                # Process stops
                stops = []
                segments = leg.get('segments', [])
                if len(segments) > 1:  # If there are multiple segments, there are stops
                    for i in range(len(segments) - 1):
                        current_segment = segments[i]
                        next_segment = segments[i + 1]

                        # Calculate stop duration in hours and minutes
                        arrival_time = datetime.strptime(current_segment.get('arrival', ''), '%Y-%m-%dT%H:%M:%S')
                        departure_time = datetime.strptime(next_segment.get('departure', ''), '%Y-%m-%dT%H:%M:%S')
                        duration = departure_time - arrival_time
                        hours = int(duration.total_seconds() // 3600)
                        minutes = int((duration.total_seconds() % 3600) // 60)
                        duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

                        # Get the stop location details
                        stop_airport = current_segment.get('destination', {})
                        stop_city = stop_airport.get('parent', {}).get('name', '')
                        stop_code = stop_airport.get('displayCode', '')

                        stop = Stop(
                            airport=stop_code,
                            city=stop_city,
                            duration=duration_str
                        )
                        stops.append(stop)

                # Get price from the first pricing option
                price_amount = float(itinerary.get('price', {}).get('raw', 0))
                price_currency = "USD"  # Default to USD as per API response

                # Get origin and destination details
                origin_segment = segments[0] if segments else {}
                destination_segment = segments[-1] if segments else {}

                origin_airport = origin_segment.get('origin', {})
                destination_airport = destination_segment.get('destination', {})

                # Format duration
                duration_minutes = leg.get('durationInMinutes', 0)
                hours = duration_minutes // 60
                minutes = duration_minutes % 60
                duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

                flight = Flight(
                    id=itinerary.get('id', ''),
                    origin=Location(
                        entityId=origin_airport.get('flightPlaceId', ''),
                        skyId=origin_airport.get('displayCode', ''),
                        name=origin_airport.get('name', ''),
                        type="AIRPORT",
                        city_name=origin_airport.get('parent', {}).get('name', ''),
                        region_name="",
                        country_name=origin_airport.get('country', ''),
                        distance_to_city_value=None,
                        distance_to_city_unit=None
                    ),
                    origin_city=origin_airport.get('parent', {}).get('name', ''),
                    destination=Location(
                        entityId=destination_airport.get('flightPlaceId', ''),
                        skyId=destination_airport.get('displayCode', ''),
                        name=destination_airport.get('name', ''),
                        type="AIRPORT",
                        city_name=destination_airport.get('parent', {}).get('name', ''),
                        region_name="",
                        country_name=destination_airport.get('country', ''),
                        distance_to_city_value=None,
                        distance_to_city_unit=None
                    ),
                    destination_city=destination_airport.get('parent', {}).get('name', ''),
                    departure={
                        'date': datetime.strptime(leg.get('departure', ''), '%Y-%m-%dT%H:%M:%S').strftime('%A, %B %d'),
                        'time': datetime.strptime(leg.get('departure', ''), '%Y-%m-%dT%H:%M:%S').strftime('%I:%M%p').lower()
                    },
                    arrival={
                        'date': datetime.strptime(leg.get('arrival', ''), '%Y-%m-%dT%H:%M:%S').strftime('%A, %B %d'),
                        'time': datetime.strptime(leg.get('arrival', ''), '%Y-%m-%dT%H:%M:%S').strftime('%I:%M%p').lower()
                    },
                    airline=leg.get('carriers', {}).get('marketing', [{}])[0].get('name', ''),
                    flight_number=segments[0].get('flightNumber', '') if segments else '',
                    price=Price(
                        amount=price_amount,
                        currency=price_currency
                    ),
                    cabin_class=cabin_class,
                    stops=stops if stops else 0,
                    total_duration=duration_str,
                    itinerary_id=itinerary.get('id', ''),
                    booking_url=itinerary.get('pricingOptions', [{}])[0].get('items', [{}])[0].get('deepLink', ''),
                    session_id=response.get('sessionId', '')
                )
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

    def search_flights(
        self,
        origin: str,
        destination: str,
        date: str,
        cabin_class: str = "economy",
        adults: int = 1,
        children: int = 0,
        infants: int = 0
    ) -> List[Flight]:
        """Search for available flights.

        Args:
            origin (str): Origin airport code (e.g. "SDF")
            destination (str): Destination airport code (e.g. "LAS")
            date (str): Departure date in YYYY-MM-DD format
            cabin_class (str): Cabin class (default: economy)
            adults (int): Number of adult passengers
            children (int): Number of child passengers
            infants (int): Number of infant passengers

        Returns:
            List[Flight]: List of available flights
        """
        # First get entity IDs for origin and destination
        origin_locations = self.search_locations(origin)
        destination_locations = self.search_locations(destination)

        if not origin_locations or not destination_locations:
            raise ValueError("Could not find airport information")

        origin_location = origin_locations[0]
        destination_location = destination_locations[0]

        # Search for flights
        response = self.client.search_flights(
            origin_sky_id=origin_location.sky_id,
            destination_sky_id=destination_location.sky_id,
            origin_entity_id=origin_location.entity_id,
            destination_entity_id=destination_location.entity_id,
            date=date,
            cabin_class=cabin_class,
            adults=adults,
            children=children,
            infants=infants
        )

        if not response.get('status'):
            raise ValueError("API request failed")

        # Get flight details for each itinerary
        flights = []
        for itinerary in response.get('data', {}).get('itineraries', []):
            # Format legs for flight details request
            legs = [{
                'origin': itinerary['legs'][0]['origin']['displayCode'],
                'destination': itinerary['legs'][0]['destination']['displayCode'],
                'date': date
            }]

            # Get flight details
            details_response = self.client.get_flight_details(
                itinerary_id=itinerary['id'],
                legs=str(legs),
                session_id=response['data']['context']['sessionId']
            )

            if details_response.get('status'):
                flights.append(Flight.from_api_response(details_response))

        return flights