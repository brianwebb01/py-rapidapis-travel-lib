from typing import List
import json
from .flight import Flight

class FlightSearchResponse:
    def __init__(self, flights: List[Flight]):
        self.results = flights

    def print_results(self):
        print("\nAvailable Flights:")
        print("=" * 50)
        for i, flight in enumerate(self.results, 1):
            print(f"\nFlight Option {i}:")
            print(f"Airline: {flight.airline}")
            print(f"Flight Number: {flight.flight_number}")
            print(f"From: {flight.origin_city} ({flight.origin}) to {flight.destination_city} ({flight.destination})")
            print(f"Departure: {flight.departure['date']} at {flight.departure['time']}")
            print(f"Arrival: {flight.arrival['date']} at {flight.arrival['time']}")
            print(f"Duration: {flight.total_duration}")
            print(f"Cabin Class: {flight.cabin_class}")
            print(f"Price: {flight.price['amount']} {flight.price['currency']}")
            print(f"Trip Type: {flight.trip_type}")

            if flight.stops:
                stop = flight.stops[0]
                print(f"{len(flight.stops)} stop{'s' if len(flight.stops) > 1 else ''}, {stop.city} ({stop.airport}), {stop.duration}")
            else:
                print("Direct Flight")

            print(f"Booking URL: {flight.bookingcom_url()}")
            print("-" * 50)

    def save_to_json(self, filename: str = 'structured_flights.json'):
        with open(filename, 'w') as f:
            json.dump([flight.model_dump() for flight in self.results], f, indent=2)