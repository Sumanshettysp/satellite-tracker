# passes/n2yo_scraper.py

from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import re

from django.utils import timezone
from .models import PassEvent

# ===== REGEX PATTERNS =====
_date_re = re.compile(r"(\d{1,2})-([A-Za-z]{3})")    # 3-Dec
_time_re = re.compile(r"(\d{1,2}):([0-5][0-9])")      # 18:18
_minutes_re = re.compile(r"(\d+)\s*min")              # 5 min
_deg_re = re.compile(r"(-?\d+(?:\.\d+)?)")            # 45°, 312°, 12.5

_months = {
    m: i for i, m in enumerate(
        ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        1
    )
}

# ====== PARSERS ======

def parse_datetime(tokens):
    """
    Extract datetime from row tokens like:
    ['3-Dec', '18:18', ...]
    """
    for i, t in enumerate(tokens):
        m = _date_re.search(t)
        if m:
            day = int(m.group(1))
            mon = _months[m.group(2)]

            # Find time in nearby tokens
            for j in range(i, min(i+3, len(tokens))):
                tm = _time_re.search(tokens[j])
                if tm:
                    hour = int(tm.group(1))
                    minute = int(tm.group(2))

                    dt = datetime.now().replace(
                        month=mon, day=day,
                        hour=hour, minute=minute,
                        second=0, microsecond=0
                    )

                    # If it's in the past > 6 months → assume next year
                    if (dt - datetime.now()).days < -180:
                        dt = dt.replace(year=dt.year + 1)

                    return dt

    return None


def find_duration(tokens):
    for t in tokens:
        m = _minutes_re.search(t)
        if m:
            return int(m.group(1))
    return 0


def find_max_el(tokens):
    for t in tokens:
        m = _deg_re.search(t)
        if m:
            try:
                return float(m.group(1))
            except:
                continue
    return 0.0


# ===== MAIN SCRAPER ======
def scrape_n2yo_passes(location, satellite, days=10):
    """
    Scrapes N2YO passes for a given location and satellite.
    Returns number of imported PassEvent rows.
    """

    lat = location.latitude
    lon = location.longitude
    norad = satellite.norad_id

    url = (
        f"https://www.n2yo.com/passes/?s={norad}"
        f"&lat={lat}&lon={lon}&alt=0&tz=0&d={days}"
    )

    parsed_rows = []   # store results BEFORE inserting into DB (important!)

    # ---------- Playwright scraping ----------
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # set True once stable
        page = browser.new_page()
        page.goto(url)

        # Wait for table to load
        try:
            page.wait_for_selector("table", timeout=15000)
        except:
            print("No table found.")
            browser.close()
            return 0

        frame = page.main_frame
        rows = frame.locator("table tbody tr")
        row_count = rows.count()
        print("Rows found:", row_count)

        for i in range(row_count):
            row = rows.nth(i)
            cells = row.locator("td")

            tokens = []
            for c in range(cells.count()):
                try:
                    txt = cells.nth(c).inner_text().strip()
                except:
                    txt = ""
                if txt:
                    tokens.append(txt.replace("\n", " ").strip())

            if not tokens:
                continue

            # Parse datetime
            start_dt = parse_datetime(tokens)
            if not start_dt:
                continue

            duration = find_duration(tokens)
            max_el = find_max_el(tokens)

            end_dt = start_dt + timedelta(minutes=duration)

            # Visibility (search from end)
            visibility = "unknown"
            for t in tokens[::-1]:
                if any(w in t.lower() for w in ("visible","day","not","mag","flare")):
                    visibility = t
                    break

            parsed_rows.append({
                "start": start_dt,
                "end": end_dt,
                "duration": duration,
                "max_el": max_el,
                "visibility": visibility,
            })

        browser.close()

    # ---------- INSERT INTO DB (safe synchronous Django ORM) ----------
    imported = 0

    for row in parsed_rows:

        # Convert to timezone-aware
        start_aware = timezone.make_aware(row["start"])
        end_aware = timezone.make_aware(row["end"])

        # Check duplicate (same location+satellite+start_time)
        exists = PassEvent.objects.filter(
            location=location,
            satellite=satellite,
            start_time=start_aware
        ).exists()

        if exists:
            continue

        PassEvent.objects.create(
            location=location,
            satellite=satellite,
            start_time=start_aware,
            end_time=end_aware,
            max_elevation=row["max_el"],
            duration=row["duration"],
            visibility=row["visibility"]
        )

        imported += 1

    print(f"Imported {imported} passes")
    return imported
