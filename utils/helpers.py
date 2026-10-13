import re
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date
import json
from tenacity import retry, stop_after_attempt, wait_exponential

def generate_slug(text: str) -> str:
    """
    Generate a URL-friendly slug from a string
    
    Args:
        text: String to convert to slug
        
    Returns:
        URL-friendly slug
    """
    # Convert to lowercase
    slug = text.lower()
    
    # Replace non-alphanumeric characters with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Ensure slug is not empty
    if not slug:
        return str(uuid.uuid4())
        
    return slug

def format_phone_number(phone: str) -> str:
    """
    Format a phone number to a standard format
    
    Args:
        phone: Phone number to format
        
    Returns:
        Formatted phone number
    """
    # Remove non-numeric characters
    digits = re.sub(r'\D', '', phone)
    
    # Handle US phone numbers
    if len(digits) == 10:
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:11]}"
    
    # Return as-is if not a standard format
    return phone

def calculate_completeness(data: Dict[str, Any], required_fields: List[str]) -> float:
    """
    Calculate the completeness of a data object
    
    Args:
        data: Dictionary of data
        required_fields: List of required field names
        
    Returns:
        Completeness score between 0.0 and 1.0
    """
    if not data or not required_fields:
        return 0.0
        
    # Count non-empty fields
    filled_fields = sum(1 for field in required_fields if field in data and data[field])
    
    # Calculate completeness
    return filled_fields / len(required_fields)

def safe_json_serialize(obj: Any) -> Any:
    """
    Safely serialize objects to JSON, handling dates and UUIDs
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON-serializable object
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: safe_json_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [safe_json_serialize(item) for item in obj]
    return obj

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def retry_async_operation(func, *args, **kwargs):
    """
    Retry an async operation with exponential backoff
    
    Args:
        func: Async function to retry
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Result of the function
    """
    return await func(*args, **kwargs)

def parse_coordinates(location_str: str) -> Optional[Dict[str, float]]:
    """
    Parse coordinates from a string (e.g., "38.8951,-77.0364")
    
    Args:
        location_str: String containing coordinates
        
    Returns:
        Dictionary with lat and lng keys, or None if invalid
    """
    if not location_str:
        return None
        
    # Try to parse as "lat,lng"
    parts = location_str.split(',')
    if len(parts) == 2:
        try:
            lat = float(parts[0].strip())
            lng = float(parts[1].strip())
            return {"lat": lat, "lng": lng}
        except ValueError:
            pass
            
    return None

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length, adding ellipsis if needed
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
        
    return text[:max_length-3] + "..."