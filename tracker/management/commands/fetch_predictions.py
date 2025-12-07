# tracker/management/commands/fetch_predictions.py
from django.core.management.base import BaseCommand
from tracker.models import Location, Satellite
from scripts.fetch_predictions import fetch_predictions_for_location
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch satellite pass predictions from Heavens Above'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--location-id',
            type=int,
            help='ID of the location to fetch predictions for'
        )
        parser.add_argument(
            '--norad-ids',
            type=str,
            help='Comma-separated list of NORAD IDs'
        )
        parser.add_argument(
            '--all-locations',
            action='store_true',
            help='Fetch predictions for all locations'
        )
    
    def handle(self, *args, **options):
        if options['all_locations']:
            locations = Location.objects.all()
            for location in locations:
                self.fetch_for_location(location, options)
        elif options['location_id']:
            try:
                location = Location.objects.get(id=options['location_id'])
                self.fetch_for_location(location, options)
            except Location.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Location with ID {options['location_id']} not found"))
        else:
            # Use default if no location specified
            location = Location.objects.first()
            if location:
                self.fetch_for_location(location, options)
            else:
                self.stdout.write(self.style.ERROR("No locations found. Please create a location first."))
    
    def fetch_for_location(self, location, options):
        # Get NORAD IDs
        if options['norad_ids']:
            norad_ids = [int(id.strip()) for id in options['norad_ids'].split(',')]
        else:
            # Default to some common satellites
            norad_ids = [25544, 20580, 44713]  # ISS, Hubble, Starlink
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Fetching predictions for location: {location}"
            )
        )
        self.stdout.write(
            f"Satellites: {', '.join(str(id) for id in norad_ids)}"
        )
        
        fetch_predictions_for_location(location.id, norad_ids)
        
        self.stdout.write(
            self.style.SUCCESS("Predictions fetched successfully!")
        )