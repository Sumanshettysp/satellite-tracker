# tracker/views.py - WORKING VERSION
from iommi import Page, html

class IndexPage(Page):
    title = "Satellite Tracker"
    header = html.h1("Satellite Pass Tracker")
    welcome = html.p("Welcome! Add locations, satellites, and view pass predictions.")
    
    links = html.div(
        children={
            "add_location": html.a("Add Location", attrs__href="/add-location/"),
            "br1": html.br(),

            "add_satellite": html.a("Add Satellite", attrs__href="/add-satellite/"),
            "br2": html.br(),

            "view_locations": html.a("View Locations", attrs__href="/locations/"),
            "br3": html.br(),

            "view_satellites": html.a("View Satellites", attrs__href="/satellites/"),
            "br4": html.br(),

            "view_passes": html.a("View Pass Predictions", attrs__href="/passes/"),
            "br5": html.br(),

            "filter_passes": html.a("Filter Passes", attrs__href="/filter-passes/"),
        }
    )

# Simple functions for other pages
class AddLocationPage(Page):
    title = "Add Location"
    header = html.h1("Add New Location")
    content = html.p("Location form will go here.")
    back_link = html.a("← Back to Home", attrs__href='/')

class AddSatellitePage(Page):
    title = "Add Satellite"
    header = html.h1("Add New Satellite")
    content = html.p("Satellite form will go here.")
    back_link = html.a("← Back to Home", attrs__href='/')

class LocationsPage(Page):
    title = "Locations"
    header = html.h1("Locations")
    content = html.p("Locations list will go here.")
    back_link = html.a("← Back to Home", attrs__href='/')

class SatellitesPage(Page):
    title = "Satellites"
    header = html.h1("Satellites")
    content = html.p("Satellites list will go here.")
    back_link =html.a("← Back to Home", attrs__href='/')

class PassesPage(Page):
    title = "Upcoming Passes"
    header = html.h1("Upcoming Satellite Passes")
    content = html.p("Pass predictions will go here.")
    back_link = html.a("← Back to Home", attrs__href='/')

class FilterPassesPage(Page):
    title = "Filter Passes"
    header = html.h1("Filter Satellite Passes")
    content = html.p("Filter form and results will go here.")
    back_link = html.a("← Back to Home", attrs__href='/')

# Django view callables created from iommi Pages
index_page = IndexPage().as_view()
add_location = AddLocationPage().as_view()
add_satellite = AddSatellitePage().as_view()
locations_view = LocationsPage().as_view()
satellites_view = SatellitesPage().as_view()
passes_view = PassesPage().as_view()
filter_passes_view = FilterPassesPage().as_view()
