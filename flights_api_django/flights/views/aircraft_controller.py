# from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from ..models import Aircraft
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.core import serializers
import datetime
from .base_controller import Controller


class AircraftController(Controller):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def get_aircraft(self, aircraft_id):
        try:
            aircraft_exists = Aircraft.objects.filter(serial_no = aircraft_id).exists()
            if aircraft_exists:
                aircraft = Aircraft.objects.get(serial_no = aircraft_id)
                final_aircraft = self.clean_object(aircraft, 'serial_no')
                return JsonResponse({'aircraft': final_aircraft}, status=200)
            else:
                return JsonResponse({'message': 'Aircraft does not exist'}, status=404)
        except Exception as e:
            return JsonResponse(status=500)

    def create_aircraft(self, body):
        try:
            existing = Aircraft.objects.filter(serial_no = body['serial_no']).exists()
            if existing:
                return JsonResponse({'message': 'Aircraft not created, Serial number already exists'}, status=400)
            else:
                try:
                    new_aircraft = Aircraft.objects.create(serial_no = body['serial_no'], manufacturer = body['manufacturer'])
                    final_aircraft = self.clean_object(new_aircraft, 'serial_no')
                    return JsonResponse({'message': "Aircraft created", 'aircraft': final_aircraft}, status=200)
                except Exception as e:
                    return JsonResponse({'error': str(e).strip()}, status=500)
        except Exception as e:
            return JsonResponse(status=500)

    def update_aircraft(self, serial_no, body):
        try:
            existing = Aircraft.objects.filter(serial_no = serial_no).exists()
            if existing:
                try:
                    values_for_update = body
                    values_for_update['date_updated'] = datetime.datetime.now()
                    new_aircraft, created = Aircraft.objects.update_or_create(serial_no = serial_no, defaults = values_for_update)                          
                    final_aircraft = self.clean_object(new_aircraft, 'serial_no')
                    return JsonResponse({'message': "Aircraft updated", 'aircraft': final_aircraft}, status=200)
                except Exception as e:
                    return JsonResponse({'error': str(e).strip()}, status=500)
            else:
                return JsonResponse({'message': 'Aircraft attempted to be changed does not exist'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e).strip()}, status=500)

    def delete_aircraft(self, serial_no):
        try:
            aircraft_exists = Aircraft.objects.filter(serial_no = serial_no).exists()
            if aircraft_exists:
                try:
                    aircraft = Aircraft.objects.get(serial_no = serial_no)
                    aircraft.delete()
                    return JsonResponse({'message': 'Aircraft with serial number: {} deleted'.format(serial_no)}, status=200)
                except Exception as e:
                    return JsonResponse({'error': str(e).strip()}, status=500)
            else:
                return JsonResponse({'message': 'Aircraft does not exist'}, status=404)
        except Exception as e:
            return JsonResponse(status=500)       



@csrf_exempt
@require_http_methods(['POST'])
def post_aircraft(request):
    body = json.loads(request.body)
    aircraft_controller = AircraftController()
    response = aircraft_controller.create_aircraft(body)
    return response
    
@csrf_exempt
@require_http_methods(['GET'])
def get_aircraft(request, aircraft_id):
    aircraft_controller = AircraftController()
    response = aircraft_controller.get_aircraft(aircraft_id)
    return response

@csrf_exempt
@require_http_methods(['PUT'])
def put_aircraft(request, aircraft_id):
    body = json.loads(request.body)
    aircraft_controller = AircraftController()
    response = aircraft_controller.update_aircraft(aircraft_id, body)
    return response

@csrf_exempt
@require_http_methods(['DELETE'])
def delete_aircraft(request, aircraft_id):
    aircraft_controller = AircraftController()
    response = aircraft_controller.delete_aircraft(aircraft_id)
    return response