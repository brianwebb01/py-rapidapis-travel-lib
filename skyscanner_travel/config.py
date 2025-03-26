import os
from dotenv import load_dotenv

def get_api_key() -> str:
    """Get the Skyscanner API key from environment variables.

    Returns:
        str: The API key if found, empty string otherwise
    """
    # Load environment variables from .env file
    load_dotenv()

    # Get API key from environment
    return os.getenv('SKYSCANNER_API_KEY', '')