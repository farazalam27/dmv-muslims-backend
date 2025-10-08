from typing import Optional
import dateparser
from hijridate import Hijri
import re

HIJRI_MONTHS = {
    "muharram": 1, "safar": 2,
    "rabi al-awwal": 3, "rabi al awwal": 3, "rabi i": 3,
    "rabi al-thani": 4, "rabi al thani": 4, "rabi ii": 4,
    "jumada al-awwal": 5, "jumada al awwal": 5, "jumada i": 5,
    "jumada al-thani": 6, "jumada al thani": 6, "jumada ii": 6,
    "rajab": 7, "shaban": 8, "sha'ban": 8, "shaaban": 8,
    "ramadan": 9, "shawwal": 10,
    "dhu al-qadah": 11, "dhu al qadah": 11,
    "dhu al-hijjah": 12, "dhu al hijjah": 12,
}


def normalize_date_time(date_str: str, time_str: Optional[str] = None, tz: str = "America/New_York") -> Optional[str]:
    """
    Converts date and optional time strings into ISO 8601 datetime strings.
    - Tries Gregorian parsing (via dateparser)
    - Falls back to Hijri if Islamic month detected (and converts to Gregorian)
    """
    if not date_str:
        return None

    # 1️⃣ Try Gregorian first
    combined = f"{date_str} {time_str or ''}".strip()
    parsed = dateparser.parse(combined, settings={"TIMEZONE": tz})
    if parsed:
        return parsed.isoformat()

    # 2️⃣ Normalize text for Hijri detection
    text = date_str.lower().strip()

    # Detect Islamic month
    month_num = None
    for name, num in HIJRI_MONTHS.items():
        if name in text:
            month_num = num
            break

    if not month_num:
        return None

    # Extract day/year numbers
    numbers = re.findall(r"\d+", text)
    if not numbers:
        return None

    day, year = None, None
    for n in map(int, numbers):
        if n <= 31 and not day:
            day = n
        elif n > 1300 and not year:
            year = n

    if not (day and year):
        return None

    # 3️⃣ Handle possible Gregorian-looking year (2025 ≈ Hijri 1446)
    if year > 1600:
        # Approximate Hijri year from Gregorian
        # (This offset keeps Hijri/Gregorian years within ~579 years)
        year -= 579

    try:
        hijri_date = Hijri(year, month_num, day)
        gregorian = hijri_date.to_gregorian()
        return gregorian.isoformat()
    except Exception as e:
        print(f"⚠️ Hijri conversion failed: {e}")
        return None