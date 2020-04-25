FROM alpine:latest

# musl-dev gcc
RUN apk update && \
    apk add build-base python3 python3-dev libffi-dev libressl-dev postgresql-dev && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    ln -sf /usr/bin/pip3 usr/bin/pip && \
    pip install --upgrade pip

RUN mkdir -p /var/run/celery/
RUN addgroup app && \
    adduser --disabled-password --gecos "" --ingroup app app && \
    chown app:app /var/run/celery/

USER app

ENV PATH="/home/app/.local/bin:${PATH}"
WORKDIR app/

COPY requirements.txt .
RUN pip install --user -r requirements.txt && \
    pip install --user .

COPY shhh shhh
ENV FLASK_APP=wsgi.py
