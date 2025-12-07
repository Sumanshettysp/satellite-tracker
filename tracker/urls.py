# tracker/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_page, name='index'),
    path('add-location/', views.add_location, name='add_location'),
    path('add-satellite/', views.add_satellite, name='add_satellite'),
    path('locations/', views.locations_view, name='locations'),
    path('satellites/', views.satellites_view, name='satellites'),
    path('passes/', views.passes_view, name='passes'),
    path('filter-passes/', views.filter_passes_view, name='filter_passes'),
]