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