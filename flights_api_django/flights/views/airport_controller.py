from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from ..models import Airport
from django.views.decorators.csrf import csrf_exempt
import json
from .base_controller import Controller


class AirportController(Controller):

    def create_airport(self, body):
        try:
            if len(body['icao']) == 4:
                existing = Airport.objects.filter(icao = body['icao']).exists()
                if existing:
                    return JsonResponse({'message': 'Airport not created, airport already exists'}, status=400)
                else:
                    try:
                        new_airport = Airport.objects.create(icao = body['icao'])
                        final_airport = self.clean_object(new_airport, 'icao')
                        return JsonResponse({'message': "Airport created", 'airport': final_airport}, status=200)
                    except Exception as e:
                        return JsonResponse({'error': str(e).strip()}, status=500)
            else:
                return JsonResponse({'message': "Airport icao should be 4 characters long"}, status=400)
        except Exception as e:
            return JsonResponse(status=500)

    def get_airport(self, icao):
        try:
            airport_exists = Airport.objects.filter(icao = icao).exists()
            if airport_exists:
                airport = Airport.objects.get(icao = icao)
                final_airport = self.clean_object(airport, 'icao')
                return JsonResponse({'airport': final_airport}, status=200)
            else:
                return JsonResponse({'message': 'Airport does not exist'}, status=404)
        except Exception as e:
            return JsonResponse(status=500)
    
    # def update_airport(self):
    # No point for this function to exist because the scheam of this object only has icao which is the pk and django doesnt
    # allow us to update the pk. Maybe delete the object then create new with the 'updated' icao would be an approach we could take

    
    def delete_airport(self, icao):
        try:
            airport_exists = Airport.objects.filter(icao = icao).exists()
            if airport_exists:
                try:
                    airport = Airport.objects.get(icao = icao)
                    airport.delete()
                    return JsonResponse({'message': 'Airport with icao: {} deleted'.format(icao)}, status=200)
                except Exception as e:
                    return JsonResponse({'error': str(e).strip()}, status=500)
            else:
                return JsonResponse({'message': 'Airport does not exist'}, status=404)
        except Exception as e:
            return JsonResponse(status=500)       


@csrf_exempt
@require_http_methods(['POST'])
def create_airport(request):
    body = json.loads(request.body)
    airport_controller = AirportController()
    response = airport_controller.create_airport(body)
    return response

@csrf_exempt
@require_http_methods(['GET'])
def get_airport(request, icao):
    airport_controller = AirportController()
    response = airport_controller.get_airport(icao)
    return response

@csrf_exempt
@require_http_methods(['DELETE'])
def delete_airport(request, icao):
    airport_controller = AirportController()
    response = airport_controller.delete_airport(icao)
    return response