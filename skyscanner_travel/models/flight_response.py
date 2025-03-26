from typing import List, Dict, Optional
from pydantic import BaseModel
import json
from .flight import Flight

class FlightSearchResponse(BaseModel):
    flights: List[Flight]
    total_results: int = 0
    currency: str = "USD"
    market: str = "US"
    locale: str = "en-US"
    country_code: str = "US"

    def __str__(self) -> str:
        return f"{self.total_results} flights found"

    def print_results(self) -> None:
        print("\nAvailable Flights:")
        print("=" * 50)
        for i, flight in enumerate(self.flights, 1):
            print(f"\nFlight Option {i}:")
            print(f"Airline: {flight.airline}")
            print(f"Flight Number: {flight.flight_number}")
            print(f"From: {flight.origin_city} ({flight.origin}) to {flight.destination_city} ({flight.destination})")
            print(f"Departure: {flight.departure['date']} at {flight.departure['time']}")
            print(f"Arrival: {flight.arrival['date']} at {flight.arrival['time']}")
            print(f"Duration: {flight.total_duration}")
            print(f"Cabin Class: {flight.cabin_class}")
            print(f"Price: {flight.price.amount} {flight.price.currency}")

            if flight.stops:
                stop = flight.stops[0]
                print(f"{len(flight.stops)} stop{'s' if len(flight.stops) > 1 else ''}, {stop.city} ({stop.airport}), {stop.duration}")
            else:
                print("Direct Flight")

            if flight.booking_url:
                print(f"Booking URL: {flight.booking_url}")
            print("-" * 50)

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
            total_results=len(flights)
        )