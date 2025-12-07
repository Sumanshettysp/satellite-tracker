# passes/iommi_ui.py
from iommi import Form, Field, Table, Column, Page, actions
from iommi import render_as_view
from django.urls import reverse
from passes.models import Location, Satellite, PassEvent
from django.utils import timezone
from datetime import datetime
from .models import PassEvent

# --- Form: Add Location ---
LocationForm = Form(
    name="add_location",
    fields=dict(
        name=Field.required(False),
        latitude=Field.type(float),
        longitude=Field.type(float),
    ),
    actions__save=actions.Submit(value="Save"),
)

# --- Form: Add Satellite ---
SatelliteForm = Form(
    name="add_satellite",
    fields=dict(
        name=Field.required(False),
        norad_id=Field(type=int),
    ),
    actions__save=actions.Submit(value="Save"),
)

# --- Filter form & table for PassEvents ---
FilterForm = Form(
    name="filter_passes",
    fields=dict(
        location=Field.choice(lambda: [(l.id, l.name or f"{l.latitude},{l.longitude}") for l in Location.objects.all()], label="Location"),
        satellite=Field.choice(lambda: [(s.id, f"{s.norad_id} - {s.name or ''}") for s in Satellite.objects.all()], label="Satellite"),
        from_time=Field(type=str, required=False, label="From (YYYY-MM-DD)"),
        to_time=Field(type=str, required=False, label="To (YYYY-MM-DD)"),
    ),
    actions__filter=actions.Submit(value="Filter"),
)

PassesTable = Table(
    columns=dict(
        location=Column(field="location__name", header="Location"),
        satellite=Column(field="satellite__name", header="Satellite"),
        start_time=Column(field="start_time", header="Start"),
        end_time=Column(field="end_time", header="End"),
        duration=Column(field="duration", header="Duration (min)"),
        max_elevation=Column(field="max_elevation", header="Max El (°)"),
        visibility=Column(field="visibility", header="Visibility"),
    )
)

class PassesTable(Table):
    class Meta:
        rows = PassEvent.objects.select_related("satellite", "location").order_by("start_time")

    satellite = Column(cell=lambda row, **_: row.satellite.name)
    location = Column(cell=lambda row, **_: row.location.name)
    start_time = Column()
    end_time = Column()
    duration = Column()
    visibility = Column()

class PassesPage(Page):
    title = "Satellite Passes"

    passes_table = PassesTable()