from django.urls import path, re_path
from flights.views import aircraft_controller, airport_controller, flight_controller, report_controller
from rest_framework.documentation import include_docs_urls



urlpatterns = [
    path('aircraft/update/<str:aircraft_id>', aircraft_controller.put_aircraft),
    path('aircraft/<str:aircraft_id>', aircraft_controller.get_aircraft),
    path('aircraft', aircraft_controller.post_aircraft),
    path('aircraft/delete/<str:aircraft_id>', aircraft_controller.delete_aircraft),
    path('airport', airport_controller.create_airport),
    path('airport/<str:icao>', airport_controller.get_airport),
    path('airport/delete/<str:icao>', airport_controller.delete_airport),
    path('flight', flight_controller.create_flight),
    path('flight/delete/<int:id>', flight_controller.delete_flight),
    path('flight/<int:id>', flight_controller.get_flight),
    path('flight/update/<int:id>', flight_controller.update_flight),
    re_path(r'^interval/(?P<dep_time>\d{4}-\d{2}-\d{2}T\d{2}:\d{2})/(?P<arr_time>\d{4}-\d{2}-\d{2}T\d{2}:\d{2})', report_controller.get_flights_in_interval),
]
