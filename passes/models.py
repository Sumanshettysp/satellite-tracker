from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.IntegerField(default=0)

    def __str__(self):
        return self.name or f"({self.latitude}, {self.longitude}, {self.altitude})"


class Satellite(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    norad_id = models.IntegerField(unique=True)

    def __str__(self):
        return self.name or str(self.norad_id)


class PassEvent(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    satellite = models.ForeignKey(Satellite, on_delete=models.CASCADE)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_elevation = models.FloatField()
    duration = models.FloatField()
    visibility = models.CharField(max_length=50)
    direction = models.CharField(max_length=50, blank=True)
    source = models.CharField(max_length=50, default="N2YO")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.satellite} over {self.location} at {self.start_time}"
