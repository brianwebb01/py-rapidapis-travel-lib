from rapid_bookingcom import LocationSearch
from rapid_bookingcom.services.location_search import LocationSearchError
import json
import os

def main():
    try:
        # Example usage
        location_search = LocationSearch()
        response = location_search.search(
            query="Dallas"
        )

        response.print_results()
    except LocationSearchError as e:
        print(f"Error searching locations: {e}")

if __name__ == "__main__":
    main()