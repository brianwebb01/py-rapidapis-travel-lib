import requests
from dotenv import load_dotenv
import os
from typing import Dict, Any, Optional

class BookingAPIClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("RAPID_API_KEY")
        self.api_host = os.getenv("RAPID_API_HOST")
        self.base_url = f"https://{self.api_host}/api/v1"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host
        }

    def _make_request(self,
                     endpoint: str,
                     method: str = "GET",
                     params: Optional[Dict[str, Any]] = None,
                     data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the Booking.com API

        Args:
            endpoint: The API endpoint to call (e.g., '/flights/searchFlights')
            method: HTTP method to use (default: GET)
            params: Query parameters for the request
            data: Request body data (for POST/PUT requests)

        Returns:
            Dict containing the API response

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response is not valid JSON
        """
        url = f"{self.base_url}{endpoint}"

        # Prepare request parameters, excluding None values
        request_params = None
        if params is not None:
            filtered_params = {k: v for k, v in params.items() if v is not None}
            request_params = filtered_params if filtered_params else None

        request_data = None
        if data is not None:
            filtered_data = {k: v for k, v in data.items() if v is not None}
            request_data = filtered_data if filtered_data else None

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=request_params,
                json=request_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"API request failed: {str(e)}")
        except ValueError as e:
            raise ValueError(f"Invalid JSON response: {str(e)}")