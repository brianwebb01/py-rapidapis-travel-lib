from pydantic import BaseModel
from typing import List, Dict, Optional, Union, Any
from datetime import datetime
from urllib.parse import quote
from .location import Location

class Price(BaseModel):
    amount: float
    currency: str

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"

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
        # Handle the full response structure
        if "data" in response and "itineraries" in response["data"]:
            itinerary = response["data"]["itineraries"][0]  # Get first itinerary
            session_id = response["sessionId"]  # Get session ID from root
        else:
            # Handle individual itinerary with session ID
            itinerary = response["itinerary"]
            session_id = response["sessionId"]

        legs = itinerary["legs"]
        first_leg = legs[0]
        first_segment = first_leg["segments"][0]

        # Format departure and arrival times
        departure_time = datetime.strptime(first_leg["departure"], "%Y-%m-%dT%H:%M:%S")
        arrival_time = datetime.strptime(first_leg["arrival"], "%Y-%m-%dT%H:%M:%S")

        # Format duration - use durationInMinutes instead of duration
        duration_minutes = first_leg["durationInMinutes"]
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
                    city=current_segment["destination"]["parent"]["name"],
                    duration=stop_duration_str
                ))

        # Create Location instances
        origin = Location(
            entityId=first_leg["origin"]["entityId"],
            skyId=first_leg["origin"]["displayCode"],
            name=first_leg["origin"]["name"],
            type="AIRPORT",
            city_name=first_leg["origin"]["city"],
            region_name="",
            country_name=first_leg["origin"]["country"]
        )

        destination = Location(
            entityId=first_leg["destination"]["entityId"],
            skyId=first_leg["destination"]["displayCode"],
            name=first_leg["destination"]["name"],
            type="AIRPORT",
            city_name=first_leg["destination"]["city"],
            region_name="",
            country_name=first_leg["destination"]["country"]
        )

        # Get price information from the itinerary
        price = Price(
            amount=float(itinerary["price"]["raw"]),
            currency="USD"  # Default to USD as it's not in the API response
        )

        return cls(
            id=itinerary["id"],
            session_id=session_id,
            airline=first_leg["carriers"]["marketing"][0]["name"],
            flight_number=first_segment["flightNumber"],
            origin=origin,
            destination=destination,
            origin_city=first_leg["origin"]["city"],
            destination_city=first_leg["destination"]["city"],
            departure={
                "date": departure_time.strftime("%A, %B %d"),
                "time": departure_time.strftime("%I:%M%p").lower(),
                "iso": departure_time.isoformat()
            },
            arrival={
                "date": arrival_time.strftime("%A, %B %d"),
                "time": arrival_time.strftime("%I:%M%p").lower(),
                "iso": arrival_time.isoformat()
            },
            total_duration=duration_str,
            cabin_class="ECONOMY",  # Default to ECONOMY as it's not in the API response
            price=price,
            stops=stops,
            booking_url=None  # No booking URL available in this response
        )

    @classmethod
    def from_api_detail_response(cls, response: Dict[str, Any]) -> "Flight":
        """Create a Flight object from the detailed API response.

        Args:
            response (Dict[str, Any]): Detailed flight response from the API

        Returns:
            Flight: Flight object with detailed information
        """
        if not response.get("status"):
            raise ValueError("API request failed")

        itinerary = response["data"]["itinerary"]
        leg = itinerary["legs"][0]
        segment = leg["segments"][0]

        # Get the first pricing option
        pricing_option = itinerary["pricingOptions"][0]
        agent = pricing_option["agents"][0]

        # Format departure and arrival times
        departure_time = datetime.strptime(leg["departure"], "%Y-%m-%dT%H:%M:%S")
        arrival_time = datetime.strptime(leg["arrival"], "%Y-%m-%dT%H:%M:%S")

        # Format duration
        duration_minutes = leg["duration"]
        hours = duration_minutes // 60
        minutes = duration_minutes % 60
        duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

        # Get stops information
        stops = []
        if leg["stopCount"] > 0:
            for i in range(len(leg["segments"]) - 1):
                current_segment = leg["segments"][i]
                next_segment = leg["segments"][i + 1]
                stop_duration = datetime.strptime(next_segment["departure"], "%Y-%m-%dT%H:%M:%S") - datetime.strptime(current_segment["arrival"], "%Y-%m-%dT%H:%M:%S")
                stop_hours = int(stop_duration.total_seconds() // 3600)
                stop_minutes = int((stop_duration.total_seconds() % 3600) // 60)
                stop_duration_str = f"{stop_hours}h {stop_minutes}m" if stop_hours > 0 else f"{stop_minutes}m"
                stops.append(Stop(
                    airport=current_segment["destination"]["displayCode"],
                    city=current_segment["destination"]["city"],
                    duration=stop_duration_str
                ))

        # Get cabin class from the response if available
        cabin_class = pricing_option.get("cabinClass", "ECONOMY").upper()

        # Get currency from the response if available
        currency = pricing_option.get("currency", "USD")

        return cls(
            id=itinerary["id"],
            session_id=response["data"]["bookingSessionId"],
            airline=segment["marketingCarrier"]["name"],
            flight_number=segment["flightNumber"],
            origin=Location(
                entityId=leg["origin"]["id"],
                skyId=leg["origin"]["displayCode"],
                name=leg["origin"]["name"],
                type="AIRPORT",
                city_name=leg["origin"]["city"],
                region_name=leg["origin"].get("region", ""),
                country_name=leg["origin"].get("country", "")
            ),
            destination=Location(
                entityId=leg["destination"]["id"],
                skyId=leg["destination"]["displayCode"],
                name=leg["destination"]["name"],
                type="AIRPORT",
                city_name=leg["destination"]["city"],
                region_name=leg["destination"].get("region", ""),
                country_name=leg["destination"].get("country", "")
            ),
            origin_city=leg["origin"]["city"],
            destination_city=leg["destination"]["city"],
            departure={
                "date": departure_time.strftime("%A, %B %d"),
                "time": departure_time.strftime("%I:%M%p").lower(),
                "iso": departure_time.isoformat()
            },
            arrival={
                "date": arrival_time.strftime("%A, %B %d"),
                "time": arrival_time.strftime("%I:%M%p").lower(),
                "iso": arrival_time.isoformat()
            },
            total_duration=duration_str,
            cabin_class=cabin_class,
            price=Price(
                amount=float(agent["price"]),
                currency=currency
            ),
            stops=stops,
            booking_url=agent.get("url")
        )