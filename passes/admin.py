from django.contrib import admin
from .models import Location, Satellite, PassEvent

admin.site.register(Location)
admin.site.register(Satellite)
admin.site.register(PassEvent)