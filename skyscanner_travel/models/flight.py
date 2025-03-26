from pydantic import BaseModel
from typing import List, Dict, Optional, Union
from datetime import datetime
from urllib.parse import quote
from .location import Location

class Price(BaseModel):
    amount: float
    currency: str

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"

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

    def __str__(self) -> str:
        departure_time = self.departure['time'] if isinstance(self.departure, dict) else self.departure
        arrival_time = self.arrival['time'] if isinstance(self.arrival, dict) else self.arrival
        return f"{departure_time} - {arrival_time} ({self.total_duration}), {self.price}"

    @classmethod
    def from_api_response(cls, response: Dict) -> "Flight":
        itinerary = response['itinerary']
        leg = itinerary['legs'][0]
        segment = leg['segments'][0]
        departure_time = datetime.strptime(segment['departure'], '%Y-%m-%dT%H:%M:%S')
        arrival_time = datetime.strptime(segment['arrival'], '%Y-%m-%dT%H:%M:%S')

        origin_code = segment['origin']['displayCode']
        destination_code = segment['destination']['displayCode']

        # Extract booking URL from pricing options if available
        booking_url = None
        if 'pricingOptions' in itinerary and itinerary['pricingOptions']:
            # Get the first pricing option's first agent's URL
            first_option = itinerary['pricingOptions'][0]
            if isinstance(first_option, list) and first_option and isinstance(first_option[0], dict):
                agents = first_option[0].get('agents', [])
                if agents and isinstance(agents, list) and agents[0].get('url'):
                    booking_url = agents[0]['url']

        return cls(
            id=itinerary.get('id'),
            origin=origin_code,
            origin_city=segment['origin']['city'],
            destination=destination_code,
            destination_city=segment['destination']['city'],
            departure={
                'date': departure_time.strftime('%m/%d/%Y'),
                'time': departure_time.strftime('%I:%M %p')
            },
            arrival={
                'date': arrival_time.strftime('%m/%d/%Y'),
                'time': arrival_time.strftime('%I:%M %p')
            },
            airline=segment['carriers']['marketing'][0]['name'],
            flight_number=segment['carriers']['marketing'][0]['code'],
            price=Price(
                amount=float(itinerary['pricingOptions'][0][0]['price']['amount']),
                currency=itinerary['pricingOptions'][0][0]['price']['currency']
            ),
            cabin_class=itinerary.get('cabinClass', 'ECONOMY'),
            stops=len(leg['segments']) - 1,
            total_duration=leg['duration'],
            itinerary_id=itinerary['id'],
            booking_url=booking_url
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