#!/usr/bin/env python
# scripts/fetch_predictions.py
import os
import sys
import time
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

# Add Django project to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satellite_tracker.settings')

import django
django.setup()

from tracker.models import Location, Satellite, PassPrediction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HeavensAboveScraper:
    BASE_URL = "https://www.heavens-above.com"
    
    def __init__(self, headless=True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self.page = self.context.new_page()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def set_location(self, lat, lng, alt=0, name=""):
        """Set the observing location on Heavens Above"""
        try:
            # Go to location setting page
            self.page.goto(f"{self.BASE_URL}/SelectLocation.aspx")
            time.sleep(2)
            
            # Click on "Manual" tab
            self.page.click("a[href*='Manual']")
            time.sleep(1)
            
            # Fill location details
            self.page.fill('input[name="ctl00$cph1$txtLat"]', str(lat))
            self.page.fill('input[name="ctl00$cph1$txtLng"]', str(lng))
            self.page.fill('input[name="ctl00$cph1$txtAlt"]', str(alt))
            
            # Submit
            self.page.click('input[name="ctl00$cph1$btnSubmit"]')
            time.sleep(2)
            
            logger.info(f"Location set to: {lat}, {lng}, {alt}m")
            return True
            
        except Exception as e:
            logger.error(f"Error setting location: {e}")
            return False
    
    def get_satellite_passes(self, norad_id, days=10):
        """Get satellite passes for the next N days"""
        try:
            # Navigate to satellite pass predictions
            url = f"{self.BASE_URL}/PassSummary.aspx?satid={norad_id}"
            self.page.goto(url)
            time.sleep(3)
            
            # Parse the page content
            content = self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            passes = []
            
            # Find the table with passes (it usually has class 'standardTable')
            table = soup.find('table', class_='standardTable')
            
            if not table:
                # Try alternative table class
                table = soup.find('table', {'width': '100%', 'class': None})
            
            if table:
                rows = table.find_all('tr')[2:]  # Skip header rows
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 6:
                        try:
                            # Parse date and time
                            date_str = cols[0].text.strip()
                            time_str = cols[1].text.strip()
                            
                            # Parse brightness/magnitude
                            magnitude = cols[2].text.strip()
                            if magnitude and magnitude != 'N/A':
                                magnitude = Decimal(magnitude)
                            else:
                                magnitude = None
                            
                            # Parse start altitude/azimuth
                            start_alt_az = cols[3].text.strip()
                            start_alt, start_az = self._parse_alt_az(start_alt_az)
                            
                            # Parse highest point
                            max_alt_az = cols[4].text.strip()
                            max_alt, max_az = self._parse_alt_az(max_alt_az)
                            
                            # Parse end altitude/azimuth
                            end_alt_az = cols[5].text.strip()
                            end_alt, end_az = self._parse_alt_az(end_alt_az)
                            
                            # Determine visibility
                            visibility = self._determine_visibility(magnitude)
                            
                            # Calculate duration (simplified - would need actual times)
                            # For now, we'll estimate 5-10 minutes
                            duration = 600  # 10 minutes in seconds
                            
                            # Create datetime (simplified - would need proper date parsing)
                            now = datetime.now()
                            start_time = now + timedelta(minutes=len(passes)*15)
                            end_time = start_time + timedelta(seconds=duration)
                            
                            pass_data = {
                                'start_time': start_time,
                                'end_time': end_time,
                                'max_elevation': max_alt,
                                'duration': duration,
                                'visibility': visibility,
                                'magnitude': magnitude,
                                'start_azimuth': start_az,
                                'max_azimuth': max_az,
                                'end_azimuth': end_az,
                            }
                            passes.append(pass_data)
                            
                        except Exception as e:
                            logger.warning(f"Error parsing row: {e}")
                            continue
            
            logger.info(f"Found {len(passes)} passes for NORAD {norad_id}")
            return passes
            
        except Exception as e:
            logger.error(f"Error getting passes for NORAD {norad_id}: {e}")
            return []
    
    def _parse_alt_az(self, alt_az_str):
        """Parse altitude/azimuth string like '10° (N)'"""
        try:
            alt_match = re.search(r'(\d+)°', alt_az_str)
            az_match = re.search(r'\(([A-Z]+)\)', alt_az_str)
            
            alt = Decimal(alt_match.group(1)) if alt_match else None
            
            if az_match:
                az_dir = az_match.group(1)
                # Convert direction to degrees
                az_map = {'N': 0, 'NE': 45, 'E': 90, 'SE': 135,
                         'S': 180, 'SW': 225, 'W': 270, 'NW': 315}
                az = Decimal(az_map.get(az_dir, 0))
            else:
                az = None
                
            return alt, az
        except:
            return None, None
    
    def _determine_visibility(self, magnitude):
        """Determine visibility based on magnitude"""
        if magnitude is None:
            return 'D'  # Daylight
        elif magnitude < 4:  # Brighter than magnitude 4
            return 'V'  # Visible
        else:
            return 'N'  # Night (too faint)

def fetch_predictions_for_location(location_id, norad_ids):
    """Fetch predictions for a location and satellite list"""
    try:
        location = Location.objects.get(id=location_id)
        
        with HeavensAboveScraper(headless=True) as scraper:
            # Set location
            success = scraper.set_location(
                float(location.latitude),
                float(location.longitude),
                location.altitude,
                location.name or ""
            )
            
            if not success:
                logger.error("Failed to set location")
                return
            
            # Fetch predictions for each satellite
            for norad_id in norad_ids:
                # Get or create satellite
                satellite, created = Satellite.objects.get_or_create(
                    norad_id=norad_id,
                    defaults={'name': f"Satellite {norad_id}"}
                )
                
                if created:
                    logger.info(f"Created new satellite: {satellite}")
                
                # Get passes
                passes = scraper.get_satellite_passes(norad_id)
                
                # Save passes to database
                for pass_data in passes:
                    # Check if this pass already exists
                    existing = PassPrediction.objects.filter(
                        location=location,
                        satellite=satellite,
                        start_time=pass_data['start_time']
                    ).exists()
                    
                    if not existing:
                        PassPrediction.objects.create(
                            location=location,
                            satellite=satellite,
                            **pass_data
                        )
                
                logger.info(f"Saved {len(passes)} passes for NORAD {norad_id}")
                time.sleep(2)  # Be nice to the server
                
    except Exception as e:
        logger.error(f"Error in fetch_predictions_for_location: {e}")

def main():
    """Example usage"""
    # Create a test location if none exists
    if not Location.objects.exists():
        Location.objects.create(
            name="Test Location",
            latitude=40.7128,
            longitude=-74.0060,
            altitude=10
        )
        logger.info("Created test location")
    
    # Example satellite NORAD IDs
    # ISS: 25544, Hubble: 20580, Starlink: 44713
    norad_ids = [25544, 20580, 44713]
    
    # Get first location
    location = Location.objects.first()
    
    if location:
        fetch_predictions_for_location(location.id, norad_ids)
    else:
        logger.error("No locations found. Please create a location first.")

if __name__ == "__main__":
    main()