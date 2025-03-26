from typing import Dict, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

class Location(BaseModel):
    """Model representing a location (airport, city) from the API."""
    model_config = ConfigDict(populate_by_name=True)

    entity_id: str = Field(alias="entityId")
    code: str = Field(alias="skyId")
    name: str
    type: str = Field(alias="type")
    city_name: Optional[str] = None
    region_name: Optional[str] = None
    country_name: Optional[str] = None
    distance_to_city_value: Optional[float] = None
    distance_to_city_unit: Optional[str] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> Optional["Location"]:
        """Create a Location instance from API response data."""
        try:
            # Extract entity ID and code
            entity_id = data.get("entityId", "") or data.get("id", "")
            code = data.get("displayCode", "") or data.get("code", "")
            if not code and entity_id:
                code = entity_id.split(".")[0]

            # Extract city name
            city_name = data.get("city", {}).get("name", "") or data.get("city_name", "")
            if not city_name and data.get("type") == "CITY":
                city_name = data.get("name", "")

            # Extract region and country names
            region_name = data.get("region", {}).get("name", "") or data.get("region_name", "")
            country_name = data.get("country", {}).get("name", "") or data.get("country_name", "")

            # Extract distance to city if available
            distance_to_city = data.get("distanceToCity", None)
            distance_to_city_value = None
            distance_to_city_unit = None
            if distance_to_city:
                distance_to_city_value = distance_to_city.get("value")
                distance_to_city_unit = distance_to_city.get("unit")
            else:
                distance_to_city_value = data.get("distance_to_city_value")
                distance_to_city_unit = data.get("distance_to_city_unit")

            # Create location data dictionary
            location_data = {
                "entityId": entity_id,
                "skyId": code,
                "name": data.get("name", ""),
                "type": data.get("type", ""),
                "city_name": city_name,
                "region_name": region_name,
                "country_name": country_name,
                "distance_to_city_value": distance_to_city_value,
                "distance_to_city_unit": distance_to_city_unit
            }

            return cls(**location_data)
        except Exception as e:
            print(f"Error creating Location from API response: {e}")
            return None

    def __str__(self) -> str:
        """String representation of the location."""
        parts = [self.name]
        if self.code:
            parts.append(f"({self.code})")
        return " ".join(parts)