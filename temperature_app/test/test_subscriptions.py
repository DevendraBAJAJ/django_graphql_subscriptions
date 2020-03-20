import time, random
import asyncio
import pytest
from channels.testing import WebsocketCommunicator
from graphene_subscriptions.consumers import GraphqlSubscriptionConsumer

async def query(query, communicator, variables=None):
    await communicator.send_json_to(
        {"id": 1, "type": "start", "payload": {"query": query, "variables": variables}}
    )


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_consumer_schema_execution_works():
    communicator = WebsocketCommunicator(GraphqlSubscriptionConsumer, "/graphql/")
    connected, subprotocol = await communicator.connect()
    assert connected

    subscription = """
        subscription {
            currentTemperatureSubscribe {
                timestamp
                value
                unit
            }
        }
    """

    await query(subscription, communicator)

    response = await communicator.receive_json_from()

    assert response["payload"] == {"data": {"currentTemperatureSubscribe" : {"timestamp": int(time.time()), "value": random.randint(0, 36), "unit": "Frhrenheit"}, "errors": None} }

