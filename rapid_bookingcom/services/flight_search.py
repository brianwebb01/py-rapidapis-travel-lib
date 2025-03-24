import requests
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import Optional
from ..models.flight import Flight, Stop
from ..models.response import FlightSearchResponse

class FlightSearch:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("RAPID_API_KEY")
        self.api_host = os.getenv("RAPID_API_HOST")
        self.url = f"https://{self.api_host}/api/v1/flights/searchFlights"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host
        }

    def _format_flight_info(self, flight, cabin_class):
        # Extract basic flight information from the first segment
        segment = flight['segments'][0]
        origin = segment['departureAirport']['code']
        origin_city = segment['departureAirport']['cityName']
        destination = segment['arrivalAirport']['code']
        destination_city = segment['arrivalAirport']['cityName']

        # Determine trip type
        if len(flight['segments']) > 1:
            trip_type = "multi-city"
        elif self.return_date is not None:
            trip_type = "roundtrip"
        else:
            trip_type = "oneway"

        # Format dates and times
        departure = datetime.fromisoformat(segment['departureTime'].replace('Z', '+00:00'))
        arrival = datetime.fromisoformat(segment['arrivalTime'].replace('Z', '+00:00'))

        # Get airline information from the first leg
        airline = segment['legs'][0]['carriersData'][0]['name']
        airline_code = segment['legs'][0]['carriersData'][0]['code']
        flight_number = f"{airline_code}{segment['legs'][0]['flightInfo']['flightNumber']}"

        # Get price information from TravellerPrices
        price = flight['travellerPrices'][0]['travellerPriceBreakdown']['totalRounded']['units']
        currency = flight['travellerPrices'][0]['travellerPriceBreakdown']['totalRounded']['currencyCode']

        # Process stops
        stops = []
        for i, leg in enumerate(segment['legs'][:-1]):
            if i > 0:  # Skip first leg as it's the origin
                stop = Stop(
                    airport=leg['arrivalAirport']['code'],
                    city=leg['arrivalAirport']['cityName'],
                    duration=str(leg['totalTime'] / 60)  # Convert seconds to minutes
                )
                stops.append(stop)
            else:
                # Calculate stop duration between legs
                next_leg = segment['legs'][i + 1]
                current_arrival = datetime.fromisoformat(leg['arrivalTime'].replace('Z', '+00:00'))
                next_departure = datetime.fromisoformat(next_leg['departureTime'].replace('Z', '+00:00'))
                stop_duration = (next_departure - current_arrival).total_seconds() / 60  # Convert to minutes

                # Format stop duration
                hours = int(stop_duration // 60)
                minutes = int(stop_duration % 60)
                duration_str = f"{hours}h {minutes}m"

                stop = Stop(
                    airport=leg['arrivalAirport']['code'],
                    city=leg['arrivalAirport']['cityName'],
                    duration=duration_str
                )
                stops.append(stop)

        # Format total duration
        total_minutes = segment['totalTime'] / 60
        total_hours = int(total_minutes // 60)
        total_minutes = int(total_minutes % 60)
        total_duration = f"{total_hours}h {total_minutes}m"

        return Flight(
            origin=origin,
            origin_city=origin_city,
            destination=destination,
            destination_city=destination_city,
            departure={
                'date': departure.strftime('%m/%d/%Y'),
                'time': departure.strftime('%I:%M %p')
            },
            arrival={
                'date': arrival.strftime('%m/%d/%Y'),
                'time': arrival.strftime('%I:%M %p')
            },
            airline=airline,
            flight_number=flight_number,
            price={
                'amount': price,
                'currency': currency
            },
            cabin_class=cabin_class,
            stops=stops,
            total_duration=total_duration,
            token=flight['token'],
            trip_type=trip_type
        )

    def search(self,
               origin: str,
               destination: str,
               depart_date: str,
               return_date: Optional[str] = None,
               cabin_class: str = "ECONOMY",
               adults: str = "1",
               children: str = "0,17",
               sort: str = "BEST",
               currency_code: str = "USD",
               page_no: str = "1"):

        self.return_date = return_date  # Store for use in _format_flight_info

        # Build query parameters
        from_id = f"{origin}.AIRPORT"
        to_id = f"{destination}.AIRPORT"

        querystring = {
            "fromId": from_id,
            "toId": to_id,
            "departDate": depart_date,
            "returnDate": return_date,
            "pageNo": page_no,
            "adults": adults,
            "children": children,
            "sort": sort,
            "cabinClass": cabin_class,
            "currency_code": currency_code
        }

        # Make API call
        response = requests.get(self.url, headers=self.headers, params=querystring)
        data = response.json()

        # Process results
        if isinstance(data, dict) and 'data' in data and isinstance(data['data'], dict):
            flights_data = data['data']
            if 'flightOffers' in flights_data:
                flights = flights_data['flightOffers']
                structured_flights = [self._format_flight_info(flight, cabin_class) for flight in flights]
                return FlightSearchResponse(structured_flights)
            else:
                raise ValueError("No flight offers found in the response data.")
        else:
            raise ValueError("No flight data found in the response or unexpected response structure.")