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

    # Example 1: Search for flights between two cities
    print("\nSearching for flights from London to Paris:")
    # Get tomorrow's date
    tomorrow = datetime.now() + timedelta(days=1)
    date_str = tomorrow.strftime("%Y-%m-%d")

    results = flight_search.search(
        origin="London",
        destination="Paris",
        date=date_str,
        adults=1,
        cabin_class="economy"
    )
    results.print_results()

    # Example 2: Get flight details for a specific itinerary
    if results and results.itineraries:
        print("\nGetting details for the first flight:")
        itinerary = results.itineraries[0]
        details = flight_search.get_flight_details(itinerary)
        details.print_results()

    # Example 3: Search for flights with specific criteria
    print("\nSearching for business class flights from New York to Tokyo:")
    results = flight_search.search(
        origin="New York",
        destination="Tokyo",
        date=date_str,
        adults=1,
        cabin_class="business"
    )
    results.print_results()

if __name__ == "__main__":
    main()