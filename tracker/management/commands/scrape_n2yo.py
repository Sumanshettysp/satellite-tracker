from django.core.management.base import BaseCommand
from passes.models import Location, Satellite
from passes.n2yo_scraper import scrape_n2yo_passes

class Command(BaseCommand):
    help = "Scrapes satellite passes from N2YO"

    def add_arguments(self, parser):
        parser.add_argument("location_id", type=int)
        parser.add_argument("satellite_id", type=int)

    def handle(self, *args, **options):
        try:
            loc = Location.objects.get(id=options["location_id"])
        except:
            self.stdout.write(self.style.ERROR("Invalid location ID"))
            return

        try:
            sat = Satellite.objects.get(id=options["satellite_id"])
        except:
            self.stdout.write(self.style.ERROR("Invalid satellite ID"))
            return

        self.stdout.write("Scraping N2YO passes...")

        imported = scrape_n2yo_passes(loc, sat)

        self.stdout.write(self.style.SUCCESS(f"Imported {imported} passes"))
