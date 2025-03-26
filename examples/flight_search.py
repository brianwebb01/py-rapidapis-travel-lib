from skyscanner_travel.services.flight_search import FlightSearch
from skyscanner_travel.services.skyscanner_client import SkyscannerClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("SKYSCANNER_API_KEY")
if not api_key:
    raise ValueError("SKYSCANNER_API_KEY environment variable is not set")

# Initialize the client and flight search
client = SkyscannerClient(api_key)
flight_search = FlightSearch(client)

# Search for flights
response = flight_search.search(
    origin_sky_id="SDF",
    destination_sky_id="LAS",
    origin_entity_id="95673969",
    destination_entity_id="95673753",
    date="2025-03-30"
)

# Print the results using the response's print_results method
response.print_results()

if response.flights:
    flight = response.flights[0]

    # Get flight details
    flight_details = flight_search.get_flight_details(flight)
    print("\nFlight Details:")
    print("=" * 50)
    print(f"Airline: {flight_details.airline} {flight_details.flight_number}")
    print(f"From: {flight_details.origin_city} ({flight_details.origin.code})")
    print(f"To: {flight_details.destination_city} ({flight_details.destination.code})")
    print(f"Departure: {flight_details.departure['date']} at {flight_details.departure['time']}")
    print(f"Arrival: {flight_details.arrival['date']} at {flight_details.arrival['time']}")
    print(f"Duration: {flight_details.total_duration}")
    print(f"Cabin Class: {flight_details.cabin_class}")
    print(f"Price: {flight_details.price}")
    if flight_details.stops:
        print(f"\nStops ({len(flight_details.stops)}):")
        for i, stop in enumerate(flight_details.stops, 1):
            print(f"{i}. {stop.city} ({stop.airport}) - {stop.duration}")
    else:
        print("Direct flight")
    if flight_details.booking_url:
        print(f"\nBook at: {flight_details.booking_url}")
    print("=" * 50)
