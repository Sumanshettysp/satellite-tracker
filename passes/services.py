import os
import requests
from datetime import datetime, timezone
from django.db import transaction
from .models import Location, Satellite, PassEvent

N2YO_BASE_URL = "https://api.n2yo.com/rest/v1/satellite"


def fetch_visual_passes_n2yo(
    norad_id: int,
    location: Location,
    days: int = 10,
    min_visibility: int = 60,
    observer_alt: int = 0,
):
    api_key = os.getenv("N2YO_API_KEY")
    if not api_key:
        raise RuntimeError("N2YO_API_KEY missing in .env file")

    url = (
        f"{N2YO_BASE_URL}/visualpasses/"
        f"{norad_id}/{location.latitude}/{location.longitude}/{observer_alt}/"
        f"{days}/{min_visibility}/?apiKey={api_key}"
    )

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    satname = data.get("info", {}).get("satname") or str(norad_id)

    satellite, _ = Satellite.objects.get_or_create(
        norad_id=norad_id,
        defaults={"name": satname},
    )

    passes = data.get("passes", [])
    if not passes:
        return

    with transaction.atomic():
        for p in passes:
            start_utc = datetime.fromtimestamp(p["startUTC"], tz=timezone.utc)
            end_utc = datetime.fromtimestamp(p["endUTC"], tz=timezone.utc)
            max_el = p.get("maxEl", 0.0)
            duration = p.get("duration", 0)
            mag = p.get("mag")
            visibility = f"mag={mag}" if mag is not None else "unknown"

            PassEvent.objects.get_or_create(
                location=location,
                satellite=satellite,
                start_time=start_utc,
                end_time=end_utc,
                defaults={
                    "max_elevation": max_el,
                    "duration": duration,
                    "visibility": visibility,
                },
            )
