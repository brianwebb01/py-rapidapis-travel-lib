from typing import Dict, Optional, Any
from pydantic import BaseModel, Field

class Location(BaseModel):
    """Model representing a location (airport, city) from the API."""
    entity_id: str = Field(alias="entityId")
    code: str = Field(alias="skyId")
    name: str
    type: str = Field(alias="entityType")
    city_name: Optional[str] = None
    region_name: Optional[str] = None
    country_name: Optional[str] = None
    distance_to_city_value: Optional[float] = None
    distance_to_city_unit: Optional[str] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> Optional["Location"]:
        """Create a Location instance from API response data."""
        try:
            # Extract data from the nested structure
            presentation = data.get("presentation", {})
            navigation = data.get("navigation", {})

            # Create location data dictionary
            location_data = {
                "entityId": data.get("entityId", ""),
                "skyId": data.get("skyId", ""),
                "name": presentation.get("title", ""),
                "entityType": navigation.get("entityType", ""),
                "city_name": navigation.get("localizedName", ""),
                "region_name": None,  # Not available in current API response
                "country_name": presentation.get("subtitle", ""),
                "distance_to_city_value": None,  # Not available in current API response
                "distance_to_city_unit": None  # Not available in current API response
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