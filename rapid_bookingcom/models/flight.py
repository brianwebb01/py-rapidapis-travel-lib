from pydantic import BaseModel
from typing import List
from urllib.parse import quote

class Stop(BaseModel):
    airport: str
    city: str
    duration: str

class Flight(BaseModel):
    origin: str
    origin_city: str
    destination: str
    destination_city: str
    departure: dict
    arrival: dict
    airline: str
    flight_number: str
    price: dict
    cabin_class: str
    stops: List[Stop]
    total_duration: str
    token: str
    trip_type: str

    def bookingcom_url(self) -> str:
        """
        Generate a booking URL for the flight.

        Returns:
            str: The booking URL for the flight.
        """
        # Format the route part of the URL
        route = f"{self.origin}.AIRPORT-{self.destination}.AIRPORT"

        # Format the date from MM/DD/YYYY to YYYY-MM-DD
        date_parts = self.departure['date'].split('/')
        formatted_date = f"{date_parts[2]}-{date_parts[0]}-{date_parts[1]}"

        # URL encode the location names
        from_location = quote(f"{self.origin_city} International Airport")
        to_location = quote(f"{self.destination_city} International Airport")

        # Construct the base URL with parameters
        base_url = "https://flights.booking.com/flights"
        params = {
            "type": "ONEWAY",
            "adults": "1",
            "cabinClass": self.cabin_class,
            "children": "",
            "from": f"{self.origin}.AIRPORT",
            "to": f"{self.destination}.AIRPORT",
            "fromCountry": "US",
            "toCountry": "US",
            "fromLocationName": from_location,
            "toLocationName": to_location,
            "depart": formatted_date,
            "sort": "BEST",
            "travelPurpose": "leisure",
            "ca_source": "flights_index_sb",
            "aid": "304142",
            "label": "gen173nr-1FCAEoggI46AdIM1gEaJYCiAEBmAExuAEHyAEN2AEB6AEB-AECiAIBqAIDuAKkqoi_BsACAdICJDcyN2ZiYTIwLWY3YjctNDMwMS1hOGIwLTAzYjhiOTQ2ZTRhMdgCBeACAQ"
        }

        # Construct the query string
        query_string = "&".join(f"{k}={v}" for k, v in params.items())

        # Combine all parts with the token
        return f"{base_url}/{route}/{self.token}/?{query_string}"