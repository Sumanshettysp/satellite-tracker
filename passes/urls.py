from django.urls import path
from .views import passes_table_view
from .views import passes_list

app_name = "passes"

urlpatterns = [
    path("add-location/", passes_table_view.add_location_view, name="add_location"),
    path("add-satellite/", passes_table_view.add_satellite_view, name="add_satellite"),
    path("pass-events/", passes_table_view.filter_passes_view, name="filter_passes"),
    path("passes/", passes_list, name="passes_list"),
]

