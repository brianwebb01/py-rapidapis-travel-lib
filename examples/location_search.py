from skyscanner_travel.services.location_search import LocationSearch
from skyscanner_travel.config import get_api_key

def main():
    # Get API key
    api_key = get_api_key()
    if not api_key:
        print("Error: SKYSCANNER_API_KEY environment variable not set")
        return

    # Create location search service
    location_search = LocationSearch(api_key)

    # Test searches
    test_queries = ["Las Vegas", "JFK", "London Heathrow"]
    for query in test_queries:
        print(f"\nSearching for '{query}':")
        try:
            response = location_search.search(query)
            response.print_results()
        except Exception as e:
            print(f"Error searching for '{query}': {e}")

if __name__ == "__main__":
    main()