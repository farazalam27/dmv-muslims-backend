# core/schema.py
from typing import List, Optional, Dict
from pydantic import BaseModel


class Location(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None
    address: Optional[str] = None


class Event(BaseModel):
    title: str
    date: Optional[str] = None
    time: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    speaker: Optional[str] = None
    audience: Optional[str] = None


class Masjid(BaseModel):
    entity_type: str = "masjid"
    name: str
    location: Optional[Location] = None
    contact: Optional[Dict[str, str]] = None
    prayer_times: Optional[Dict[str, str]] = None
    events: List[Event] = []
    donation_link: Optional[str] = None
    source: Optional[str] = None