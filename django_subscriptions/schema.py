import graphene

from temperature_app.schema import TemperatureSubscription, TemperatureQuery, TemperatureCreatedSubscription


class Query(TemperatureQuery, graphene.ObjectType):
    pass


class Subscription(TemperatureSubscription, TemperatureCreatedSubscription, graphene.ObjectType):
    pass


schema = graphene.Schema(
    query=Query,
    subscription=Subscription
)