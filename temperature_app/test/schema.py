import graphene
import time, random
from rx import Observable


class TemperatureType(graphene.ObjectType):
    timestamp = graphene.Int()
    value = graphene.Int()
    unit = graphene.String()


class TestSubscription(graphene.ObjectType):
    current_temperature_subscribe = graphene.Field(TemperatureType)

    def resolve_current_temperature_subscribe(self, info):
        return Observable.interval(3000)\
            .map(lambda i: TemperatureType(timestamp=int(time.time()), value=random.randint(0, 36), unit="Fahrenheit"))


class Query(graphene.ObjectType):
    base = graphene.String()


schema = graphene.Schema(query=Query, subscription=TestSubscription)
