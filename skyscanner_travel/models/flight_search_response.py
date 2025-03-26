from typing import List, Optional
from pydantic import BaseModel
from .flight import Flight

class FlightSearchResponse(BaseModel):
    flights: List[Flight]
    total_results: int
    currency: str
    market: str
    locale: str
    country_code: str

    def __str__(self) -> str:
        return f"{len(self.flights)} flights found"

    def print_results(self) -> None:
        print("\nAvailable Flights:")
        print("=" * 50 + "\n")
        for i, flight in enumerate(self.flights, 1):
            print(f"Flight {i}:")
            print(flight)
            print("-" * 50 + "\n")