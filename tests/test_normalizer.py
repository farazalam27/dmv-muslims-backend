# tests/test_normalizer.py
from core.normalizer import normalize_date_time


def test_normalize_date_and_time_valid():
    result = normalize_date_time("Oct 10 2025", "7pm")
    assert result is not None
    assert result.startswith("2025-10-10")


# tests/test_normalizer.py
def test_normalize_date_only():
    result = normalize_date_time("Ramadan 15 2025")
    assert result is not None
    assert "2025" in result or "2026" in result  # Hijri conversion may overlap Gregorian year

def test_invalid_date_returns_none():
    result = normalize_date_time("", "5pm")
    assert result is None