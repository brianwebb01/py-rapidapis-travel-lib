from rapid_bookingcom import FlightSearch

def main():
    # Example usage
    flight_search = FlightSearch()
    response = flight_search.search(
        origin="SDF",
        destination="LAS",
        depart_date="2025-03-30"
    )
    response.print_results()

if __name__ == "__main__":
    main()