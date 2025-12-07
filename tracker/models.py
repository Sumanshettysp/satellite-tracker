# tracker/models.py
from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    altitude = models.IntegerField(default=0, help_text="Altitude in meters")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name', 'created_at']
    
    def __str__(self):
        if self.name:
            return f"{self.name} ({self.latitude}, {self.longitude})"
        return f"Location ({self.latitude}, {self.longitude})"

class Satellite(models.Model):
    norad_id = models.IntegerField(unique=True, verbose_name="NORAD ID")
    name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['norad_id']
    
    def __str__(self):
        if self.name:
            return f"{self.name} ({self.norad_id})"
        return f"Satellite {self.norad_id}"

class PassPrediction(models.Model):
    VISIBILITY_CHOICES = [
        ('V', 'Visible'),
        ('D', 'Daylight'),
        ('N', 'Night'),
    ]
    
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='predictions')
    satellite = models.ForeignKey(Satellite, on_delete=models.CASCADE, related_name='predictions')
    
    # Pass details
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_elevation = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Max Elevation (°)")
    duration = models.IntegerField(help_text="Duration in seconds")
    visibility = models.CharField(max_length=1, choices=VISIBILITY_CHOICES)
    
    # Additional data
    start_azimuth = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    max_azimuth = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    end_azimuth = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    magnitude = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    # Metadata
    fetched_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=50, default='heavens-above')
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['start_time', 'end_time']),
            models.Index(fields=['location', 'satellite']),
        ]
    
    def __str__(self):
        return f"{self.satellite} over {self.location} at {self.start_time}"