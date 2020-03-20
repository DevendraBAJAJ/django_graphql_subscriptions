import time
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from graphene_subscriptions.signals import post_save_subscription



class Temperature(models.Model):
    timestamp = models.IntegerField(max_length=11, default=int(time.time()))
    value = models.CharField(max_length=3)
    unit = models.CharField(max_length=12, default='Fahrenheit')


post_save.connect(post_save_subscription, sender=Temperature, dispatch_uid="temperature_post_save")
