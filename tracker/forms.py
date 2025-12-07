# tracker/forms.py
from iommi import Form, Field
from django import forms as django_forms
from tracker.models import Location, Satellite, PassPrediction

class LocationForm(Form):
    class Meta:
        model = Location
        fields = ['name', 'latitude', 'longitude', 'altitude']
        
    @classmethod
    def get_instance(cls, request, **kwargs):
        # For creating new locations
        return None

class SatelliteForm(Form):
    class Meta:
        model = Satellite
        fields = ['norad_id', 'name', 'description']
        
    @classmethod
    def get_instance(cls, request, **kwargs):
        # For creating new satellites
        return None

class FilterForm(Form):
    location = Field.choice(
        choices=lambda form, field: [(None, 'All')] + 
            [(loc.id, str(loc)) for loc in Location.objects.all()],
        required=False,
    )
    
    satellite = Field.choice(
        choices=lambda form, field: [(None, 'All')] + 
            [(sat.id, str(sat)) for sat in Satellite.objects.all()],
        required=False,
    )
    
    from_time = Field.datetime(
        required=False,
        label="From Time",
        attrs={'type': 'datetime-local'},
    )
    
    to_time = Field.datetime(
        required=False,
        label="To Time",
        attrs={'type': 'datetime-local'},
    )
    
    class Meta:
        title = "Filter Satellite Passes"
        actions__submit__display_name = "Filter"
        
    def on_submit(self):
        # This form will be used in the view to filter results
        pass