# tests/test_masjid_site_agent.py
import pytest
from agents.masjid_site_agent import _extract_events, Masjid, Event


def test_extract_events_finds_titles():
    sample_html = """
    <div class="event">
      <h3>Youth Halaqa</h3>
      <p>Every Friday after Maghrib</p>
    </div>
    <div class="event">
      <h3>Community BBQ</h3>
    </div>
    """
    events = _extract_events(sample_html)
    assert len(events) == 2
    assert any("Youth Halaqa" in e.title for e in events)
    assert isinstance(events[0], Event)