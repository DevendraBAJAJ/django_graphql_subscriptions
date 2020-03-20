from graphene_django import DjangoObjectType
from graphene_subscriptions.events import CREATED
from rx import Observable
import graphene
import random, time

from temperature_app.models import Temperature


class TemperatureType(DjangoObjectType):
    class Meta:
        model = Temperature


class TemperatureQuery(object):
    current_temperature = graphene.Field(
        TemperatureType,
        timestamp=graphene.Int(),
        value=graphene.Int(),
        unit=graphene.String()
    )

    def resolve_current_temperature(self, info, **kwargs):
        return Temperature.objects.last()


class TemperatureSubscription(graphene.ObjectType):
    current_temperature_subscribe = graphene.Field(
        TemperatureType,
        timestamp=graphene.Int(),
        value=graphene.Int(),
        unit=graphene.String()
    )

    def resolve_current_temperature_subscribe(self, info):
        return Observable.interval(1000)\
            .map(lambda i: TemperatureType(
                    timestamp=int(time.time()),
                    value=random.randint(0, 36),
                    unit="Fahrenheit")
                 )


class TemperatureCreatedSubscription(graphene.ObjectType):
    temperature_created = graphene.Field(TemperatureType)

    def resolve_temperature_created(root, info):
        return root.filter(
            lambda event:
                event.operation == CREATED and
                isinstance(event.instance, Temperature)
        ).map(lambda event: event.instance)