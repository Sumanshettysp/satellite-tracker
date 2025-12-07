# tracker/admin.py
from django.contrib import admin
from tracker.models import Location, Satellite, PassPrediction

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'altitude', 'created_at')
    search_fields = ('name',)

@admin.register(Satellite)
class SatelliteAdmin(admin.ModelAdmin):
    list_display = ('norad_id', 'name', 'created_at', 'updated_at')
    search_fields = ('norad_id', 'name')

@admin.register(PassPrediction)
class PassPredictionAdmin(admin.ModelAdmin):
    list_display = ('satellite', 'location', 'start_time', 'end_time', 
                   'max_elevation', 'visibility')
    list_filter = ('visibility', 'location', 'satellite')
    search_fields = ('satellite__name', 'satellite__norad_id')
    date_hierarchy = 'start_time'