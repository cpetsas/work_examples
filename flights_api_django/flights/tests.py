from django.test import TestCase
from .models import Aircraft, Airport, Flight
from .views.airport_controller import AirportController
from .views.flight_controller import FlightController
from .views.aircraft_controller import AircraftController
from .views.report_controller import ReportController
import json

class AirportTests(TestCase):
    
    def test_airport_creation(self):
        airport_controller = AirportController()
        response = airport_controller.create_airport(body={"icao": "zxcv"})
        self.assertEqual(response.status_code, 200)

    def test_get_airport(self):
        airport_controller = AirportController()
        response = airport_controller.create_airport(body={"icao": "zxcv"})
        response = airport_controller.get_airport(icao= "zxcv")
        self.assertEqual(response.status_code, 200)

    def test_delete_airport(self):
        airport_controller = AirportController()
        response = airport_controller.create_airport(body={"icao": "zxcv"})
        response_delete = airport_controller.delete_airport(icao='zxcv')
        responses = [response.status_code, response_delete.status_code]
        self.assertEqual(responses,[200,200])
    
    def test_airport_creation_fail(self):
        airport_controller = AirportController()
        response = airport_controller.create_airport(body={"icao": "zxcv"})
        response_same_airport = airport_controller.create_airport(body={"icao": "zxcv"})
        response_long_airport = airport_controller.create_airport(body={"icao": "zxczzzv"})
        response_short_airport = airport_controller.create_airport(body={"icao": "zx"})
        responses_codes = [response.status_code,response_same_airport.status_code, response_long_airport.status_code, response_short_airport.status_code]
        responses_messages = [json.loads(response.content)['message'],json.loads(response_same_airport.content)['message'], json.loads(response_long_airport.content)['message'], json.loads(response_short_airport.content)['message']]
        self.assertEqual(responses_messages, ["Airport created", 'Airport not created, airport already exists', "Airport icao should be 4 characters long", "Airport icao should be 4 characters long"])
        self.assertEqual(responses_codes, [200,400,400,400])

    def test_get_aiport_fail(self):
        airport_controller = AirportController()
        response = airport_controller.create_airport(body={"icao": "zxcv"})
        response_nonexistant = airport_controller.get_airport(icao= "zxlv")
        responses_codes = [response_nonexistant.status_code]
        responses_messages = [json.loads(response_nonexistant.content)['message']]
        self.assertEqual(responses_messages, ['Airport does not exist'])
        self.assertEqual(responses_codes, [404])
    
    def test_delete_airport_fail(self):
        airport_controller = AirportController()
        response = airport_controller.create_airport(body={"icao": "zxcv"})
        response_nonexistant = airport_controller.delete_airport(icao='zxcp')
        responses_codes = [response_nonexistant.status_code]
        responses_messages = [json.loads(response_nonexistant.content)['message']]
        self.assertEqual(responses_messages, ['Airport does not exist'])
        self.assertEqual(responses_codes, [404])


        
class AircraftTest(TestCase):

    def test_aircraft_creation(self):
        aircraft_controller = AircraftController()
        response = aircraft_controller.create_aircraft(body={"serial_no": "serial", "manufacturer": "manufacturer"})
        self.assertEqual(response.status_code, 200)

    def test_get_aircraft(self):
        aircraft_controller = AircraftController()
        response = aircraft_controller.create_aircraft(body={"serial_no": "serial", "manufacturer": "manufacturer"})
        response_get = aircraft_controller.get_aircraft(aircraft_id= 'serial')
        self.assertEqual(response_get.status_code, 200)
    
    def test_update_aircraft(self):
        aircraft_controller = AircraftController()
        aircraft_controller.create_aircraft(body={"serial_no": "serial", "manufacturer": "manufacturer"})
        response_update = aircraft_controller.update_aircraft(serial_no= 'serial', body={"serial_no": "serial", "manufacturer": "manufaturer"})
        self.assertEqual(response_update.status_code, 200)

    def test_delete_aircraft(self):
        aircraft_controller = AircraftController()
        aircraft_controller.create_aircraft(body={"serial_no": "serial", "manufacturer": "manufacturer"})
        response_delete = aircraft_controller.delete_aircraft(serial_no= 'serial')
        self.assertEqual(response_delete.status_code, 200)

    def test_aircraft_creation_fail(self):
        aircraft_controller = AircraftController()
        aircraft_controller.create_aircraft(body={"serial_no": "serial", "manufacturer": "manufacturer"})
        response = aircraft_controller.create_aircraft(body={"serial_no": "serial", "manufacturer": "manufacturer"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)['message'], 'Aircraft not created, Serial number already exists')

    def test_aircraft_get_fail(self):
        aircraft_controller = AircraftController()
        response = aircraft_controller.get_aircraft(aircraft_id= 'serial')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)['message'], 'Aircraft does not exist')

    def test_update_aircraft_fail(self):
        aircraft_controller = AircraftController()
        response = aircraft_controller.update_aircraft(serial_no= 'serial', body={"serial_no": "serial", "manufacturer": "manufacturer"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)['message'], 'Aircraft attempted to be changed does not exist')

    def test_delete_aircraft_fail(self):
        aircraft_controller = AircraftController()
        response = aircraft_controller.delete_aircraft(serial_no= 'serial')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)['message'], 'Aircraft does not exist')


class FlightTest(TestCase):

    def setUp(self):
        flight_controller = FlightController()
        aircraft_controller = AircraftController()
        airport_controller = AirportController()
        response = aircraft_controller.create_aircraft(body={"serial_no": "hello", "manufacturer": "manufacturer"})
        airport_controller.create_airport(body={"icao": "assa"})
        airport_controller.create_airport(body={"icao": "asdf"})

    def test_flight_creation(self):
        flight_controller = FlightController()
        response = flight_controller.create_flight(body={  "serial_no": "hello",
                                                "departure_time": "2122-01-31 15:45",
                                                "arrival_time": "2122-01-31 16:30",
                                                "departure_airport": "assa",
                                                "arrival_airport": "asdf"
                                                })
        self.assertEqual(response.status_code, 200)

    def test_get_flight(self):
        flight_controller = FlightController()
        response = flight_controller.create_flight(body={  "serial_no": "hello",
                                                "departure_time": "2122-01-31 15:45",
                                                "arrival_time": "2122-01-31 16:30",
                                                "departure_airport": "assa",
                                                "arrival_airport": "asdf"
                                                })
        response = flight_controller.get_flight(json.loads(response.content)['flight']['id'])
        self.assertEqual(response.status_code, 200)

    def test_update_flight(self):
        flight_controller = FlightController()
        response = flight_controller.create_flight(body={  "serial_no": "hello",
                                                "departure_time": "2122-01-31 15:45",
                                                "arrival_time": "2122-01-31 16:30",
                                                "departure_airport": "assa",
                                                "arrival_airport": "asdf"
                                                })
        response_update = flight_controller.update_flight(json.loads(response.content)['flight']['id'] ,{  "serial_no": "hello",
                                                "departure_time": "2122-01-31 15:45",
                                                "arrival_time": "2122-01-31 16:30",
                                                "departure_airport": "asdf",
                                                "arrival_airport": "assa"
                                                })
        self.assertEqual(response_update.status_code, 200)

    def test_delete_flight(self):
        flight_controller = FlightController()
        response = flight_controller.create_flight(body={  "serial_no": "hello",
                                                "departure_time": "2122-01-31 15:45",
                                                "arrival_time": "2122-01-31 16:30",
                                                "departure_airport": "assa",
                                                "arrival_airport": "asdf"
                                                })
        response_delete = flight_controller.delete_flight(json.loads(response.content)['flight']['id'])
        self.assertEqual(response_delete.status_code, 200)

    def test_create_fail(self):
        flight_controller = FlightController()
        response = flight_controller.create_flight(body={  "serial_no": "hello",
                                                "departure_time": "2022-01-31 15:45",
                                                "arrival_time": "2022-01-31 16:30",
                                                "departure_airport": "assa",
                                                "arrival_airport": "asdf"
                                                })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)['message'], 'Flight cannot be created because flights need to be scheduled for the future')
        flight_controller.create_flight(body={  "serial_no": "hello",
                                                "departure_time": "2122-01-31 15:45",
                                                "arrival_time": "2122-01-31 16:30",
                                                "departure_airport": "assa",
                                                "arrival_airport": "asdf"
                                                })
        response = flight_controller.create_flight(body={  "serial_no": "hello",
                                                "departure_time": "2122-01-31 16:00",
                                                "arrival_time": "2122-01-31 16:30",
                                                "departure_airport": "assa",
                                                "arrival_airport": "asdf"
                                                })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)['message'], 'Flight cannot be created because the specific aircraft is busy')

    def test_update_fail(self):
        flight_controller = FlightController()
        response = flight_controller.update_flight(id = 1, body={  "serial_no": "hello",
                                                "departure_time": "2122-01-31 15:45",
                                                "arrival_time": "2122-01-31 16:30",
                                                "departure_airport": "assa",
                                                "arrival_airport": "asdf"
                                                })
        self.assertEqual(json.loads(response.content)['message'], 'flight does not exist')
        response = flight_controller.create_flight(body={  "serial_no": "hello",
                                                "departure_time": "2122-01-31 15:45",
                                                "arrival_time": "2122-01-31 16:30",
                                                "departure_airport": "assa",
                                                "arrival_airport": "asdf"
                                                })
        response = flight_controller.update_flight(id=json.loads(response.content)['flight']['id'], body={  "serial_no": "hello",
                                                "departure_time": "2122-01-31 15:45",
                                                "arrival_time": "2122-01-31 16:30",
                                                "arrival_airport": "asdf"
                                                })
        self.assertEqual(json.loads(response.content)['message'], 'Please include departure_airport in the request')
        response = flight_controller.create_flight(body={  "serial_no": "hello",
                                                "departure_time": "2122-01-31 18:00",
                                                "arrival_time": "2122-01-31 19:30",
                                                "departure_airport": "assa",
                                                "arrival_airport": "asdf"
                                                })
        response = flight_controller.update_flight(id=json.loads(response.content)['flight']['id'], body={  "serial_no": "hello",
                                                "departure_time": "2122-01-31 16:00",
                                                "arrival_time": "2122-01-31 16:30",
                                                "departure_airport": "assa",
                                                "arrival_airport": "asdf"
                                                })
        self.assertEqual(json.loads(response.content)['message'], 'Flight cannot be edited because the specific aircraft is busy')

    def test_get_flight_fail(self):
        flight_controller = FlightController()
        response = flight_controller.get_flight(id = 1)
        self.assertEqual(json.loads(response.content)['message'], 'flight does not exist')

class ReportTest(TestCase):

    def setUp(self):
        flight_controller = FlightController()
        aircraft_controller = AircraftController()
        airport_controller = AirportController()
        response = aircraft_controller.create_aircraft(body={"serial_no": "hello", "manufacturer": "manufacturer"})
        response = aircraft_controller.create_aircraft(body={"serial_no": "hi", "manufacturer": "manufacturer"})
        response = aircraft_controller.create_aircraft(body={"serial_no": "hey", "manufacturer": "manufacturer"})
        airport_controller.create_airport(body={"icao": "assa"})
        airport_controller.create_airport(body={"icao": "asdf"})
        airport_controller.create_airport(body={"icao": "ssss"})
        response = flight_controller.create_flight(body={  "serial_no": "hello",
                                                "departure_time": "2122-01-31 12:45",
                                                "arrival_time": "2122-01-31 13:30",
                                                "departure_airport": "assa",
                                                "arrival_airport": "asdf"
                                                })
        response = flight_controller.create_flight(body={  "serial_no": "hi",
                                                "departure_time": "2122-01-31 13:45",
                                                "arrival_time": "2122-01-31 19:30",
                                                "departure_airport": "assa",
                                                "arrival_airport": "asdf"
                                                })
        response = flight_controller.create_flight(body={  "serial_no": "hey",
                                                "departure_time": "2122-01-31 14:45",
                                                "arrival_time": "2122-01-31 16:00",
                                                "departure_airport": "ssss",
                                                "arrival_airport": "asdf"
                                                })
        response = flight_controller.create_flight(body={  "serial_no": "hello",
                                                "departure_time": "2122-01-31 15:45",
                                                "arrival_time": "2122-01-31 17:30",
                                                "departure_airport": "asdf",
                                                "arrival_airport": "assa"
                                                })
        response = flight_controller.create_flight(body={  "serial_no": "hi",
                                                "departure_time": "2122-01-31 15:45",
                                                "arrival_time": "2122-01-31 16:30",
                                                "departure_airport": "asdf",
                                                "arrival_airport": "ssss"
                                                })
        response = flight_controller.create_flight(body={  "serial_no": "hey",
                                                "departure_time": "2122-01-31 16:15",
                                                "arrival_time": "2122-01-31 17:30",
                                                "departure_airport": "asdf",
                                                "arrival_airport": "assa"
                                                })
                                
    def test_report(self):
        report_controller = ReportController()
        response = report_controller.get_flights_in_interval('2122-01-31T12:00', '2122-01-31T17:00')
        self.assertEqual(json.loads(response.content), {'assa': {'number_of_flights': 2, 'in_flight_time': 240.0}, 'ssss': {'number_of_flights': 1, 'in_flight_time': 75.0}, 'asdf': {'number_of_flights': 2, 'in_flight_time': 120.0}})