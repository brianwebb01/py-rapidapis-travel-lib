from pydantic import BaseModel
from typing import List

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