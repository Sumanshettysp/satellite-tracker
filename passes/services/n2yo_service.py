import requests
from datetime import datetime, timedelta
from django.utils import timezone

from passes.models import PassEvent


N2YO_BASE_URL = "https://api.n2yo.com/rest/v1/satellite/visualpasses"


def fetch_10_day_passes(location, satellite, api_key):
    """
    Fetch and store next 10 days satellite passes
    """

    url = (
        f"{N2YO_BASE_URL}/"
        f"{satellite.norad_id}/"
        f"{location.latitude}/"
        f"{location.longitude}/"
        f"{location.altitude}/"
        f"10/10/"  # 10 DAYS, min 10 sec visibility
        f"{api_key}"
    )

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    passes = data.get("passes", [])
    imported = 0

    for p in passes:
        start_time = datetime.fromtimestamp(p["startUTC"], tz=timezone.utc)
        end_time = datetime.fromtimestamp(p["endUTC"], tz=timezone.utc)

        #Avoid duplicates
        exists = PassEvent.objects.filter(
            satellite=satellite,
            location=location,
            start_time=start_time,
        ).exists()

        if exists:
            continue

        PassEvent.objects.create(
            satellite=satellite,
            location=location,
            start_time=start_time,
            end_time=end_time,
            duration=p["duration"],
            max_elevation=p["maxEl"],
            visibility=p["mag"],
            direction=f"{p['startAz']}° → {p['endAz']}°",
            source="N2YO API",
        )

        imported += 1

    return imported
