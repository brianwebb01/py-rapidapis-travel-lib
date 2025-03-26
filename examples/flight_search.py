from skyscanner_travel.services.flight_search import FlightSearch
from skyscanner_travel.services.skyscanner_client import SkyscannerClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Initialize the client with your API key
    client = SkyscannerClient(api_key=os.getenv('SKYSCANNER_API_KEY'))

    # Create a flight search service
    flight_search = FlightSearch(client)

    # Example: Search for flights between Louisville (SDF) and Las Vegas (LAS)
    print("\nSearching for flights from Louisville to Las Vegas:")
    # Get tomorrow's date
    tomorrow = datetime.now() + timedelta(days=1)
    date_str = tomorrow.strftime("%Y-%m-%d")

    # Using the exact parameters from the working example
    results = flight_search.search(
        origin_sky_id="SDF",  # Louisville International Airport
        destination_sky_id="LAS",  # Las Vegas McCarran International Airport
        origin_entity_id="95673969",
        destination_entity_id="95673753",
        date=date_str,
        adults=1,
        children=0,
        infants=0,
        cabin_class="economy",
        currency="USD",
        market="en-US",
        country_code="US"
    )

    # Print search results
    print(f"\nFound {len(results.flights)} flights:")
    for i, flight in enumerate(results.flights, 1):
        print(f"\n{i}. {flight.airline} {flight.flight_number}")
        print(f"    From: {flight.origin_city} ({flight.origin.code})")
        print(f"    To: {flight.destination_city} ({flight.destination.code})")
        print(f"    Departure: {flight.departure['date']} at {flight.departure['time']}")
        print(f"    Arrival: {flight.arrival['date']} at {flight.arrival['time']}")
        print(f"    Duration: {flight.total_duration}")

        # Handle stops information
        if isinstance(flight.stops, list) and flight.stops:
            print(f"    Stops: {len(flight.stops)}")
            for j, stop in enumerate(flight.stops, 1):
                print(f"       Stop {j}: {stop.city} ({stop.airport}) {stop.duration}")

        else:
            print("    Stops: Direct")

        print(f"    Price: {flight.price.amount:.2f} {flight.price.currency}")
        if flight.booking_url:
            print(f"    Booking URL: {flight.booking_url}")


if __name__ == "__main__":
    main()