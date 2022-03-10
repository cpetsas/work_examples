from django.db import models
from django.utils.timezone import now
from django.db.models import CheckConstraint, Q, F


class Aircraft(models.Model):
    serial_no = models.CharField(max_length=20, primary_key=True)
    manufacturer = models.CharField(max_length=50)
    date_created = models.DateTimeField(default=now)
    date_updated = models.DateTimeField(default=now)

class Airport(models.Model):
    icao = models.CharField(max_length=4, primary_key=True)

class Flight(models.Model):
    departure_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='dep_airport')
    arrival_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arr_airport')
    departure_time = models.DateTimeField(null=False, default=now)
    arrival_time = models.DateTimeField(null=False, default=now)
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE)


