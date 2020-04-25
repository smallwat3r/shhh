FROM alpine:latest

# musl-dev gcc
RUN apk update && \
    apk add build-base python3 python3-dev libffi-dev libressl-dev postgresql-dev && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    ln -sf /usr/bin/pip3 usr/bin/pip && \
    pip install --upgrade pip

RUN addgroup app && \
    adduser --disabled-password --gecos "" --ingroup app app

USER app
ENV PATH="/home/app/.local/bin:${PATH}"

COPY requirements.txt .
RUN pip install --user -r requirements.txt

WORKDIR app
COPY . .
RUN pip install --user .

ENV FLASK_APP=wsgi.py
