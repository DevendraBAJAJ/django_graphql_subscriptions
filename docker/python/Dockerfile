FROM python:3.7.7
MAINTAINER dmbajaj.bajaj@gmail.com

copy . /django_subscriptions

WORKDIR /django_subscriptions

RUN pip3 install -r requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

