from .services.flight_search import FlightSearch

def main():
    # Example usage
    search = FlightSearch()

    # Example search parameters
    origin = "SDF"
    destination = "LAS"
    depart_date = "2024-04-01"
    return_date = "2024-04-05"

    try:
        # Perform the search
        results = search.search(
            origin=origin,
            destination=destination,
            depart_date=depart_date,
            return_date=return_date
        )

        # Print results
        results.print_results()

        # Save results to JSON
        results.save_to_json()

    except Exception as e:
        print(f"Error performing flight search: {str(e)}")

if __name__ == "__main__":
    main()