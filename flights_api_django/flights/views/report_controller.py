from ..models import Flight, Aircraft, Airport
from .base_controller import Controller
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from django.db.models import Q
from datetime import datetime
from django.db.models import Count, Sum


class ReportController(Controller):

    def get_flights_in_interval(self, dep_time, arr_time):
        try:
            departure_time = datetime.fromisoformat(dep_time)
            arrival_time = datetime.fromisoformat(arr_time)
            flights_in_interval = list(Flight.objects.filter((Q(departure_time__gte=departure_time) & Q(departure_time__lte=arrival_time)) | (Q(arrival_time__lte=arrival_time) & Q(arrival_time__gte=departure_time))).values().annotate(Count('departure_airport_id')).order_by())
            airport_details = {}
            for flight in flights_in_interval:
                if flight['departure_airport_id'] not in airport_details:
                    airport_details[flight['departure_airport_id']] = { 'number_of_flights': 1,
                                                                        'in_flight_time': 0}
                else:
                    airport_details[flight['departure_airport_id']]['number_of_flights'] = airport_details[flight['departure_airport_id']]['number_of_flights'] + 1
                if departure_time >= flight['departure_time']:
                    min_departure = departure_time
                    flight_time_in_interval = (flight['arrival_time'] - min_departure).seconds / 60
                elif arrival_time <= flight['arrival_time']:
                    min_arrival = arrival_time
                    flight_time_in_interval = (min_arrival - flight['departure_time']).seconds / 60
                else:
                    flight_time_in_interval = (flight['arrival_time'] - flight['departure_time']).seconds / 60
                airport_details[flight['departure_airport_id']]['in_flight_time'] = airport_details[flight['departure_airport_id']]['in_flight_time'] + flight_time_in_interval 
            return JsonResponse(airport_details, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e).strip()}, status=500)


@csrf_exempt
@require_http_methods(['GET'])
def get_flights_in_interval(request, dep_time, arr_time):
    report_controller = ReportController()
    response = report_controller.get_flights_in_interval(dep_time, arr_time)
    return response
