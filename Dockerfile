FROM python:3.8-slim

RUN pip install --upgrade pip
ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD . /src
WORKDIR /src
CMD ./manage.py runserver 0.0.0.0:8000
