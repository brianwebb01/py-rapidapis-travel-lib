from pydantic import BaseModel
from typing import List, Dict, Optional, Union
from datetime import datetime
from urllib.parse import quote
from .location import Location

class Price(BaseModel):
    amount: float
    currency: str

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"

    def __getitem__(self, key):
        return getattr(self, key)

class Stop(BaseModel):
    city: str
    airport: str
    duration: str

class Flight(BaseModel):
    """Model representing a flight from Skyscanner."""

    id: str
    session_id: str
    airline: str
    flight_number: str
    origin: Location
    destination: Location
    origin_city: str
    destination_city: str
    departure: Dict[str, str]
    arrival: Dict[str, str]
    total_duration: str
    cabin_class: str
    price: Price
    stops: List[Stop]
    booking_url: Optional[str] = None

    @property
    def itinerary_id(self) -> str:
        return self.id

    def __str__(self) -> str:
        departure_time = self.departure['time']
        arrival_time = self.arrival['time']
        return f"{departure_time} - {arrival_time} ({self.total_duration}), {self.price}"

    @classmethod
    def from_api_response(cls, response: Dict) -> "Flight":
        itinerary = response["itinerary"]
        legs = itinerary["legs"]
        first_leg = legs[0]
        first_segment = first_leg["segments"][0]

        # Format departure and arrival times
        departure_time = datetime.strptime(first_leg["departure"], "%Y-%m-%dT%H:%M:%S")
        arrival_time = datetime.strptime(first_leg["arrival"], "%Y-%m-%dT%H:%M:%S")

        # Format duration
        duration_minutes = first_leg["duration"]
        hours = duration_minutes // 60
        minutes = duration_minutes % 60
        duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

        # Get stops information
        stops = []
        if first_leg["stopCount"] > 0:
            for i in range(len(first_leg["segments"]) - 1):
                current_segment = first_leg["segments"][i]
                next_segment = first_leg["segments"][i + 1]
                stop_duration = datetime.strptime(next_segment["departure"], "%Y-%m-%dT%H:%M:%S") - datetime.strptime(current_segment["arrival"], "%Y-%m-%dT%H:%M:%S")
                stop_hours = int(stop_duration.total_seconds() // 3600)
                stop_minutes = int((stop_duration.total_seconds() % 3600) // 60)
                stop_duration_str = f"{stop_hours}h {stop_minutes}m" if stop_hours > 0 else f"{stop_minutes}m"
                stops.append(Stop(
                    airport=current_segment["destination"]["displayCode"],
                    city=current_segment["destination"]["city"],
                    duration=stop_duration_str
                ))

        # Get price information
        price_option = itinerary["pricingOptions"][0]
        agent = price_option["agents"][0]

        # Create Location instances
        origin = Location.from_api_response(first_leg["origin"])
        if origin is None:
            origin = Location(
                entityId=first_leg["origin"]["id"],
                skyId=first_leg["origin"]["displayCode"],
                name=first_leg["origin"]["name"],
                type="AIRPORT",
                city_name=first_leg["origin"]["city"],
                region_name="",
                country_name=""
            )

        destination = Location.from_api_response(first_leg["destination"])
        if destination is None:
            destination = Location(
                entityId=first_leg["destination"]["id"],
                skyId=first_leg["destination"]["displayCode"],
                name=first_leg["destination"]["name"],
                type="AIRPORT",
                city_name=first_leg["destination"]["city"],
                region_name="",
                country_name=""
            )

        return cls(
            id=itinerary["id"],
            session_id=response.get("sessionId", "default_session"),
            airline=first_segment["marketingCarrier"]["name"],
            flight_number=first_segment["flightNumber"],
            origin=origin,
            destination=destination,
            origin_city=first_leg["origin"]["city"],
            destination_city=first_leg["destination"]["city"],
            departure={
                "date": departure_time.strftime("%A, %B %d"),
                "time": departure_time.strftime("%I:%M%p").lower()
            },
            arrival={
                "date": arrival_time.strftime("%A, %B %d"),
                "time": arrival_time.strftime("%I:%M%p").lower()
            },
            total_duration=duration_str,
            cabin_class="ECONOMY",  # Default to ECONOMY as it's not in the API response
            price=Price(
                amount=float(agent["price"]),
                currency="USD"  # Default to USD as it's not in the API response
            ),
            stops=stops,
            booking_url=agent.get("url")
        )