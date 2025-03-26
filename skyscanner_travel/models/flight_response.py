from typing import List, Dict, Optional
from pydantic import BaseModel
import json
from .flight import Flight

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
            print(f"\n{i}. {flight.airline} {flight.flight_number}")
            print(f"   ID: {flight.id} Session ID: {flight.session_id}")
            print(f"   From: {flight.origin_city} ({flight.origin.code})")
            print(f"   To: {flight.destination_city} ({flight.destination.code})")
            print(f"   Departure: {flight.departure['date']} at {flight.departure['time']}")
            print(f"   Arrival: {flight.arrival['date']} at {flight.arrival['time']}")
            print(f"   Duration: {flight.total_duration}")

            if isinstance(flight.stops, list) and flight.stops:
                print(f"   Stops: {len(flight.stops)}")
                for j, stop in enumerate(flight.stops, 1):
                    print(f"      {j}. {stop.city} ({stop.airport}) - {stop.duration}")
            else:
                print("   Direct flight")

            print(f"   Price: {flight.price}")
            if flight.booking_url:
                print(f"   Book at: {flight.booking_url}")

    def save_to_json(self, filename: str = 'structured_flights.json') -> None:
        with open(filename, 'w') as f:
            json.dump([flight.model_dump() for flight in self.flights], f, indent=2)

    @classmethod
    def from_api_response(cls, response: Dict) -> "FlightSearchResponse":
        flights = []
        if "itineraries" in response:
            for itinerary in response["itineraries"]:
                flights.append(Flight.from_api_response({"itinerary": itinerary}))
        return cls(
            flights=flights,
            total_results=len(flights),
            currency="USD",
            market="US",
            locale="en-US",
            country_code="US"
        )