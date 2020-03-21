## GraphQl Subscriptions with Django

A simpl implementation of Graphene + Django + Django Channels which showcases on how Graphql subscriptions can be used in a Django Project. This project demonstrates a simple service that generates a temperature every second to which we can subscribe and get real time updates and also demonstrates an example of subscriptions when a new object is created in your database using the Django post_save signals.

## Dependencies

1. graphene-subscriptions
2. graphene-django
3. django-channels
4. graphql-playground
5. Also check requirements.txt file in the repo for other packages


## Screenshots

![image](https://user-images.githubusercontent.com/16799932/77150402-cda72a00-6ab9-11ea-8701-c5a2127ed3ef.png)

![image](https://user-images.githubusercontent.com/16799932/77150298-96d11400-6ab9-11ea-815f-15f44c50f664.gif)


## Setup

1. We are using django-channels, graphene-subscriptions and graphene-django so we need to add them to our installed apps
   ```python
   INSTALLED_APPS = [
          .....
          .....
          'channels',
          'graphene_subscriptions',
          'graphene_django',
          'graphql_playground',
          .....
          .....
   ]
   ```
   
2. We are using an in-memory Channel Layer in our dev server so add that to your settings. For more info check: [Django Channels installation docs](https://channels.readthedocs.io/en/latest/installation.html) and [Channel Layers](https://channels.readthedocs.io/en/latest/topics/channel_layers.html)   
   

    ```python
    # django_graphql_subscriptions/settings.py
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        }
    }
    ```
    
  
3. Setting our project's urls with the graphql-playground url and our project's graphql endpoint.

    ```python
    from django.contrib import admin
    from django.urls import path
    from django.views.decorators.csrf import csrf_exempt
    from graphene_django.views import GraphQLView
    from graphql import GraphQLCoreBackend
    from graphql_playground.views import GraphQLPlaygroundView


    class GraphQLCustomCoreBackend(GraphQLCoreBackend):
        def __init__(self, executor=None):
            # type: (Optional[Any]) -> None
            super().__init__(executor)
            self.execute_params['allow_subscriptions'] = True

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('graphql-playground/', csrf_exempt(GraphQLPlaygroundView.as_view())),
        path('temp-sub/', csrf_exempt(GraphQLView.as_view(graphiql=True, backend=GraphQLCustomCoreBackend()))),
    ]
    ``` 
    * Note: Here we have a custom class `GraphQLCustomCoreBackend` which inherits from `GraphQLCoreBackend` which is then         passed as a `backend` argument to our `GraphQLView`. This bypasses allow_subscriptions flag that needs to be passed as an     argument which raises Subscriptions are not allowed error otherwise.
    
    

4. Add `GraphqlSubscriptionConsumer` to your `routing.py` file.

    ```python
    # django_subscriptions/routing.py
    from channels.routing import ProtocolTypeRouter, URLRouter
    from django.urls import path 

    from graphene_subscriptions.consumers import GraphqlSubscriptionConsumer

    application = ProtocolTypeRouter({
        "websocket": URLRouter([
            path('graphql-playground/', GraphqlSubscriptionConsumer)
        ]),
    })
    ```
    * Note: The path `path('graphql-playground/', GraphqlSubscriptionConsumer)` has to be similar to the                          `GraphQLPlaygroundView` url in your project's urls.py file which is necessary to establish a websocket connection for           listening to live updates and model changes.
    
    
## Deifine APP level schema 
 
Define your app level schema with Subscriptions and Queries and then later connect it to your project level schema. In the below example you have:
  - `TemperatureSubscription` which simulates timestamp, random temperature value and unit to which we can subscribe to. 
  - `TemperatureCreatedSubscription` which returns your object data everytime a new object is created in your database. You       can use this to further create UPDATE, DELETE and even CUSTOM_EVENT subscriptions.

   ```python
    # temperature_app/schema.py
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
   ``` 



## Define a Model with a post_save signal

For the post_save subscription you need to define a model with a post_save signal which inherits the post_save_subscription method from graphene_subscriptions.signals module.
 
 ```python
    # temperature_app/models.py
    import time
    from django.db import models
    from django.db.models.signals import post_save
    from graphene_subscriptions.signals import post_save_subscription

    class Temperature(models.Model):
        timestamp = models.IntegerField(max_length=11, default=int(time.time()))
        value = models.CharField(max_length=3)
        unit = models.CharField(max_length=12, default='Fahrenheit')


    post_save.connect(post_save_subscription, sender=Temperature, dispatch_uid="temperature_post_save")
``` 

## Define Project level schema.

Connect your subscriptions from above to your project schema. Import you Subscriptions and Queries to inherit from the app level schema.
    
```python
   # django_subscriptions/schema.py
    import graphene

    from temperature_app.schema import TemperatureQuery, TemperatureSubscription, TemperatureCreatedSubscription


    class Query(TemperatureQuery, graphene.ObjectType):
        pass


    class Subscription(TemperatureSubscription, TemperatureCreatedSubscription, graphene.ObjectType):
        pass


    schema = graphene.Schema(
        query=Query,
        subscription=Subscription
    )
``` 
    
## Running the Project (MacOS)

1. Using your local development server. 
   Navigate to your empty project directory on your MacOS and then:

  `git clone https://github.com/DevendraBAJAJ/django_graphql_subscriptions.git`

  `cd django_graphql_subscriptions`

  `source venv/bin/activate`

  `python manage.py runserver`

  Then navigate to:
  `http://127.0.0.1:8000/graphql-playground/` : This will open the playground interface.
  
  Within the playground interface navigate to:
  `http://127.0.0.1:8000/temp-sub/`
  


2. Using docker container

  `git clone https://github.com/DevendraBAJAJ/django_graphql_subscriptions.git`

  `cd django_graphql_subscriptions`

  `source venv/bin/activate`
  
  `docker-compose build`

  `docker-compose up`

  Then navigate to:
  `http://127.0.0.1:8000/graphql-playground/` : This will open the playground interface.
  
  Within the playground interface navigate to:
  `http://127.0.0.1:8000/temp-sub/`



