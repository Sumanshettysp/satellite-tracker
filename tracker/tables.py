# tracker/tables.py
from iommi import Table, Column
from tracker.models import Location, Satellite, PassPrediction

class LocationTable(Table):
    class Meta:
        model = Location
        columns = ['name', 'latitude', 'longitude', 'altitude', 'created_at']
        page_size = 20

class SatelliteTable(Table):
    class Meta:
        model = Satellite
        columns = ['norad_id', 'name', 'description', 'created_at']
        page_size = 20

class PassPredictionTable(Table):
    location = Column()
    satellite = Column()
    
    class Meta:
        model = PassPrediction
        columns = [
            'location',
            'satellite',
            'start_time',
            'end_time',
            'max_elevation',
            'duration',
            'visibility',
            'magnitude',
        ]
        page_size = 50