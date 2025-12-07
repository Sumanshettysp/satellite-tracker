from django.core.management.base import BaseCommand
from django.conf import settings

from passes.models import Location, Satellite
from passes.services.n2yo_service import fetch_10_day_passes


class Command(BaseCommand):
    help = "Fetch 10-day satellite pass predictions using N2YO API"

    def add_arguments(self, parser):
        parser.add_argument("location_id", type=int)
        parser.add_argument("satellite_id", type=int)

    def handle(self, *args, **options):
        location = Location.objects.get(id=options["location_id"])
        satellite = Satellite.objects.get(id=options["satellite_id"])

        self.stdout.write("Fetching 10-day pass prediction...")

        imported = fetch_10_day_passes(
            location,
            satellite,
            settings.N2YO_API_KEY,
        )

        self.stdout.write(
            self.style.SUCCESS(f"✅ Imported {imported} passes for next 10 days")
        )
