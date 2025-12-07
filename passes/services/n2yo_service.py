import requests
from datetime import datetime, timezone as dt_timezone
from django.utils import timezone
from passes.models import PassEvent

N2YO_BASE_URL = "https://api.n2yo.com/rest/v1/satellite/visualpasses"


def fetch_10_day_passes(location, satellite, api_key):
    """
    Fetch and store next 10 days satellite passes using N2YO API
    """
    days = 10
    min_visibility = 1
    url = (
        f"{N2YO_BASE_URL}/"
        f"{satellite.norad_id}/"
        f"{location.latitude}/"
        f"{location.longitude}/"
        f"{location.altitude}/"
        f"{days}/"
        f"{min_visibility}"
        f"?apiKey={api_key.strip()}"
    )
    
    response = requests.get(url, timeout=30)

    response.raise_for_status()

    # ✅ HARD SAFETY CHECK (this is missing in your run)
    if not response.text or response.text.strip() == "null":
        print("❌ N2YO returned null (invalid request or quota issue)")
        return 0

    data = response.json()

    if not isinstance(data, dict):
        print("❌ Invalid JSON structure:", data)
        return 0

    passes = data.get("passes", [])
    print("🛰️ Passes Count from API:", len(passes))

    imported = 0

    for p in passes:
        start_time = datetime.fromtimestamp(p["startUTC"], tz=dt_timezone.utc)
        end_time = datetime.fromtimestamp(p["endUTC"], tz=dt_timezone.utc)

        if PassEvent.objects.filter(
            satellite=satellite,
            location=location,
            start_time=start_time,
        ).exists():
            continue

        PassEvent.objects.create(
            satellite=satellite,
            location=location,
            start_time=start_time,
            end_time=end_time,
            duration=p.get("duration", 0),
            max_elevation=p.get("maxEl", 0),
            visibility=p.get("mag"),
            direction=f"{p.get('startAz')}° → {p.get('endAz')}°",
            source="N2YO API",
        )

        imported += 1

    return imported
