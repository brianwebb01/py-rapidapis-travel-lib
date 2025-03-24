from typing import List
from .location import Location

class LocationSearchResponse:
    def __init__(self, locations: List[Location]):
        self.locations = locations

    def print_results(self):
        print("\nAvailable Locations:")
        print("=" * 50)
        for i, location in enumerate(self.locations, 1):
            print(f"\nLocation {i}:")
            if location.type == "CITY":
                print(f"{location.code} {location.city_name or location.name} All Airports")
                print(f"{location.region_name}, {location.country_name}")
            elif location.type == "AIRPORT":
                print(f"{location.code} {location.name}")
                if location.distance_to_city_value and location.distance_to_city_unit:
                    rounded_distance = round(location.distance_to_city_value)
                    print(f"{rounded_distance} {location.distance_to_city_unit} from downtown")
                if location.city_name:
                    print(f"{location.city_name}, {location.region_name}, {location.country_name}")
                else:
                    print(f"{location.region_name}, {location.country_name}")
            print("-" * 50)