from pydantic import BaseModel
from typing import List, Dict, Optional, Union
from datetime import datetime
from urllib.parse import quote
from .location import Location

class Price(BaseModel):
    amount: float
    currency: str

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"

    def __getitem__(self, key):
        return getattr(self, key)

class Stop(BaseModel):
    airport: str
    city: str
    duration: str

class Flight(BaseModel):
    """Model representing a flight from Skyscanner."""

    id: Optional[str] = None
    origin: Union[str, Location]
    origin_city: str
    destination: Union[str, Location]
    destination_city: str
    departure: Union[str, Dict[str, str]]
    arrival: Union[str, Dict[str, str]]
    airline: str
    flight_number: str
    price: Union[Price, Dict[str, Union[float, str]]]
    cabin_class: str = "ECONOMY"
    stops: Union[List[Union[Stop, Dict[str, str]]], int] = []
    total_duration: str
    itinerary_id: str
    booking_url: Optional[str] = None
    session_id: Optional[str] = None

    def __str__(self) -> str:
        departure_time = self.departure['time'] if isinstance(self.departure, dict) else self.departure
        arrival_time = self.arrival['time'] if isinstance(self.arrival, dict) else self.arrival
        return f"{departure_time} - {arrival_time} ({self.total_duration}), {self.price}"

    @classmethod
    def from_api_response(cls, response: Dict) -> "Flight":
        itinerary = response['itinerary']
        leg = itinerary['legs'][0]
        segment = leg['segments'][0]

        # Format departure and arrival times
        departure_time = datetime.strptime(segment['departure'], '%Y-%m-%dT%H:%M:%S')
        arrival_time = datetime.strptime(segment['arrival'], '%Y-%m-%dT%H:%M:%S')

        # Format duration
        duration_minutes = leg.get('duration', 0)
        hours = duration_minutes // 60
        minutes = duration_minutes % 60
        duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

        # Get origin and destination details
        origin = segment['origin']
        destination = segment['destination']

        # Get price and booking URL from itinerary
        pricing_option = itinerary.get('pricingOptions', [{}])[0]
        agent = pricing_option.get('agents', [{}])[0]
        price_amount = float(agent.get('price', 0))
        price_currency = "USD"  # Default to USD as per API response
        booking_url = agent.get('url', '')

        # Get city names from the API response
        origin_city = origin.get('city', '')
        destination_city = destination.get('city', '')

        # Get stops information
        stops = []
        if leg.get('stopCount', 0) > 0:
            for stop in leg.get('stops', []):
                stops.append(Stop(
                    airport=stop.get('displayCode', ''),
                    city=stop.get('city', {}).get('name', ''),
                    duration=stop.get('duration', '')
                ))

        return cls(
            id=itinerary.get('id'),
            origin=Location(
                entityId=origin.get('id', ''),
                skyId=origin.get('displayCode', ''),
                name=origin.get('name', ''),
                type="AIRPORT",
                city_name=origin_city,
                region_name="",
                country_name=origin.get('country', ''),
                distance_to_city_value=None,
                distance_to_city_unit=None
            ),
            origin_city=origin_city,
            destination=Location(
                entityId=destination.get('id', ''),
                skyId=destination.get('displayCode', ''),
                name=destination.get('name', ''),
                type="AIRPORT",
                city_name=destination_city,
                region_name="",
                country_name=destination.get('country', ''),
                distance_to_city_value=None,
                distance_to_city_unit=None
            ),
            destination_city=destination_city,
            departure={
                'date': departure_time.strftime('%A, %B %d'),
                'time': departure_time.strftime('%I:%M%p').lower()
            },
            arrival={
                'date': arrival_time.strftime('%A, %B %d'),
                'time': arrival_time.strftime('%I:%M%p').lower()
            },
            airline=segment.get('marketingCarrier', {}).get('name', ''),
            flight_number=segment.get('flightNumber', ''),
            price=Price(
                amount=price_amount,
                currency=price_currency
            ),
            cabin_class=itinerary.get('cabinClass', 'ECONOMY'),
            stops=stops,
            total_duration=duration_str,
            itinerary_id=itinerary.get('id', ''),
            booking_url=booking_url,
            session_id=response.get('sessionId', '')
        )

class FlightSearchResponse(BaseModel):
    flights: List[Flight]
    total_results: int
    currency: str
    market: str
    locale: str
    country_code: str

    def __str__(self) -> str:
        return f"Found {self.total_results} flights"

    def print_results(self) -> None:
        print(f"\nFound {self.total_results} flights:")
        for i, flight in enumerate(self.flights, 1):
            print(f"\n{i}. {flight}")
            if flight.booking_url:
                print(f"   Book at: {flight.booking_url}")