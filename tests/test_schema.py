# tests/test_schema.py
import pytest
from core.schema import Masjid, Event, Location


def test_event_model_validation():
    e = Event(
        title="Friday Halaqa",
        date="2025-10-10",
        time="19:00",
        description="Weekly youth halaqa",
        image_url="https://example.com/flyer.png",
        speaker="Imam Ahmad"
    )
    assert e.title == "Friday Halaqa"
    assert "2025-10-10" in e.date


def test_masjid_with_events():
    m = Masjid(
        name="Dar Al Hijrah",
        location=Location(address="3159 Row St, Falls Church, VA"),
        events=[
            Event(title="Friday Halaqa"),
            Event(title="Community BBQ")
        ],
        donation_link="https://donate.daralhijrah.net"
    )
    assert m.name == "Dar Al Hijrah"
    assert m.events[0].title == "Friday Halaqa"
    assert "Falls Church" in m.location.address