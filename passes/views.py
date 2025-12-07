# passes/views.py
from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import HttpResponse
#from iommi import render_as_view
from iommi import Table
from .models import Pass
from .iommi_ui import LocationForm, SatelliteForm, FilterForm, PassesTable, PassesPage
from .models import Location, Satellite, PassEvent
from django.utils import timezone
from datetime import datetime

passes_list_view = PassesPage().as_view()
passes_table = Table(auto__model=Pass) 
passes_table_view = passes_table.as_view()
def add_location_view(request):
    form = LocationForm.bind(request=request)
    if form.submitted and form.is_valid():
        data = form.get_bound_data()
        Location.objects.create(
            name=data.get("name") or "",
            latitude=float(data["latitude"]),
            longitude=float(data["longitude"]),
        )
        return redirect(reverse("passes:filter_passes"))
    return render(request, "passes/iommi_page.html", {"iommi_object": form})

def add_satellite_view(request):
    form = SatelliteForm.bind(request=request)
    if form.submitted and form.is_valid():
        data = form.get_bound_data()
        Satellite.objects.create(
            name=data.get("name") or "",
            norad_id=int(data["norad_id"]),
        )
        return redirect(reverse("passes:filter_passes"))
    return render(request, "passes/iommi_page.html", {"iommi_object": form})

def filter_passes_view(request):
    form = FilterForm.bind(request=request)
    # compute queryset base
    qs = PassEvent.objects.select_related("location", "satellite").order_by("start_time")
    if form.submitted and form.is_valid():
        bd = form.get_bound_data()
        if bd.get("location"):
            qs = qs.filter(location_id=int(bd["location"]))
        if bd.get("satellite"):
            qs = qs.filter(satellite_id=int(bd["satellite"]))
        # optional date filters
        from_time = bd.get("from_time")
        to_time = bd.get("to_time")
        if from_time:
            qs = qs.filter(start_time__gte=datetime.fromisoformat(from_time))
        if to_time:
            qs = qs.filter(start_time__lte=datetime.fromisoformat(to_time))
    # Bind table with queryset
    table = PassesTable.bind(request=request, data_source=qs)
    # Show both filter form and table
    return render(request, "passes/filter_page.html", {"form": form, "table": table})

def passes_list(request):
    passes = (
        PassEvent.objects
        .select_related("satellite", "location")
        .order_by("start_time")
    )

    return render(
        request,
        "passes/passes_list.html",
        {"passes": passes}
    )

