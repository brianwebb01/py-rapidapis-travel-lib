from pydantic import BaseModel, Field, model_validator
from typing import Optional

class Location(BaseModel):
    id: str
    type: str
    name: str
    code: str
    region_name: str = Field(alias="regionName")
    country_name: str = Field(alias="countryName")
    city_name: Optional[str] = Field(alias="cityName", default=None)
    distance_to_city_value: Optional[float] = None
    distance_to_city_unit: Optional[str] = None

    @model_validator(mode='before')
    def extract_distance(cls, values):
        if isinstance(values, dict):
            distance = values.get('distanceToCity', {})
            if isinstance(distance, dict):
                values['distance_to_city_value'] = distance.get('value')
                values['distance_to_city_unit'] = distance.get('unit')
        return values