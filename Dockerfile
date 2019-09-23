FROM python:3.6-alpine

ENV PYTHONUNBUFFERED 1
ENV FLASK_APP habraproxy/app.py
ENV FLASK_ENV development

RUN apk update \
    && apk add gcc python3-dev libc-dev libxml2-dev libxslt-dev

COPY ./requirements /requirements
RUN pip install --upgrade pip \
    && pip install -r /requirements/production.txt --no-cache

COPY . /app
WORKDIR /app

EXPOSE 5000
