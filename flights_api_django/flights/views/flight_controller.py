from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from ..models import Flight, Aircraft, Airport
from django.views.decorators.csrf import csrf_exempt
import json
from .base_controller import Controller
from django.db.models import Q
from datetime import datetime


class FlightController(Controller):

    def create_flight(self, body):
        try:
            clashes = self.perform_checks(body)
            if type(clashes) == list:
                if len(clashes) == 0:
                    try:
                        departure_time = datetime.fromisoformat(body['departure_time'])
                        arrival_time = datetime.fromisoformat(body['arrival_time'])
                        dep_airport = Airport.objects.get(icao = body['departure_airport'])
                        arr_airport = Airport.objects.get(icao = body['arrival_airport'])
                        aircraft = Aircraft.objects.get(serial_no = body['serial_no'])
                        new_flight = Flight.objects.create(departure_airport = dep_airport, arrival_airport = arr_airport, departure_time = departure_time, arrival_time = arrival_time, aircraft = aircraft)
                        final_flight = self.clean_object(new_flight, 'id')
                        return JsonResponse({'message': "flight created", 'flight': final_flight}, status=200)
                    except Exception as e:
                        return JsonResponse({'error': str(e).strip()}, status=500)
                else:
                    return JsonResponse({'message': "Flight cannot be created because the specific aircraft is busy"}, status=400)
            else:
                return clashes
        except Exception as e:
            return JsonResponse(status=500)

    def get_flight(self, id):
        try:
            flight_exists = Flight.objects.filter(id = id).exists()
            if flight_exists:
                flight = Flight.objects.get(id = id)
                final_flight = self.clean_object(flight, 'id')
                return JsonResponse({'flight': final_flight}, status=200)
            else:
                return JsonResponse({'message': 'flight does not exist'}, status=404)
        except Exception as e:
            return JsonResponse(status=500)
    
    def update_flight(self, id, body):
        try:
            flight_exists = Flight.objects.filter(id = id).exists()
            if flight_exists:
                required_details = ['serial_no', 'departure_time', 'arrival_time', 'departure_airport', 'arrival_airport']
                for detail in required_details:
                    if detail not in body:
                        return JsonResponse({'message': 'Please include {} in the request'.format(detail)}, status=400)
                clashes = self.perform_checks(body, id=id)
                if type(clashes) == list:
                    if len(clashes) == 0:
                        try:
                            values_update = {}
                            values_update['departure_time'] = datetime.fromisoformat(body['departure_time'])
                            values_update['arrival_time'] = datetime.fromisoformat(body['arrival_time'])
                            values_update['departure_airport'] = Airport.objects.get(icao = body['departure_airport'])
                            values_update['arrival_airport'] = Airport.objects.get(icao = body['arrival_airport'])
                            values_update['aircraft'] = Aircraft.objects.get(serial_no = body['serial_no'])
                            new_flight, created = Flight.objects.update_or_create(id = id, defaults = values_update)
                            final_flight = self.clean_object(new_flight, 'id')
                            return JsonResponse({'message': "Flight updated", 'flight': final_flight}, status=200)
                        except Exception as e:
                            return JsonResponse({'error': str(e).strip()}, status=500)
                    else:
                        return JsonResponse({'message': "Flight cannot be edited because the specific aircraft is busy"}, status=400)
                else:
                    return clashes
            else:
                return JsonResponse({'message': 'flight does not exist'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e).strip()}, status=500)
    
    def delete_flight(self, id):
        try:
            flight_exists = Flight.objects.filter(id = id).exists()
            if flight_exists:
                try:
                    flight = Flight.objects.get(id = id)
                    flight.delete()
                    return JsonResponse({'message': 'flight with id: {} deleted'.format(id)}, status=200)
                except Exception as e:
                    return JsonResponse({'error': str(e).strip()}, status=500)
            else:
                return JsonResponse({'message': 'flight does not exist'}, status=404)
        except Exception as e:
            return JsonResponse(status=500)       
        
    def perform_checks(self, body, id=None):
        try:
            departure_time = datetime.fromisoformat(body['departure_time'])
            arrival_time = datetime.fromisoformat(body['arrival_time'])
            if departure_time >= arrival_time:
                return JsonResponse({'message': "Flight cannot be created because the departure time should be before the arrival time"}, status=400)
            if departure_time <= datetime.now():
                return JsonResponse({'message': "Flight cannot be created because flights need to be scheduled for the future"}, status=400)
            if id==None:
                clashes = list(Flight.objects.filter(Q(aircraft=body['serial_no']) & (Q(departure_time__lte=departure_time) & Q(arrival_time__gte=departure_time) | (Q(departure_time__lte=arrival_time) & Q(arrival_time__gte=arrival_time)))))
            else:
                clashes = list(Flight.objects.filter(Q(aircraft=body['serial_no']) & (~Q(id=id)) & (Q(departure_time__lte=departure_time) & Q(arrival_time__gte=departure_time) | (Q(departure_time__lte=arrival_time) & Q(arrival_time__gte=arrival_time)))))
            return clashes
        except Exception as e:
            return JsonResponse({'error': str(e).strip()}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def create_flight(request):
    body = json.loads(request.body)
    flight_controller = FlightController()
    response = flight_controller.create_flight(body)
    return response

@csrf_exempt
@require_http_methods(['GET'])
def get_flight(request, id):
    flight_controller = FlightController()
    response = flight_controller.get_flight(id)
    return response

@csrf_exempt
@require_http_methods(['DELETE'])
def delete_flight(request, id):
    flight_controller = FlightController()
    response = flight_controller.delete_flight(id)
    return response

@csrf_exempt
@require_http_methods(['PUT'])
def update_flight(request, id):
    body = json.loads(request.body)
    flight_controller = FlightController()
    response = flight_controller.update_flight(id, body)
    return response