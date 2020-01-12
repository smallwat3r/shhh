# -*- coding: utf-8 -*-
# File     : Dockerfile
# Date     : 18.09.2019
# Author   : Austin Schaffer <schaffer.austin.t@gmail.com>
# Last edit: Matthieu Petiteau <mpetiteau.pro@gmail.com>

FROM alpine:3.8

RUN apk update && \
    apk add build-base python3 python3-dev libffi-dev libressl-dev && \
    cd /usr/bin && \
    ln -sf python3 python && \
    ln -sf pip3 pip && \
    pip install --upgrade pip

# EXPOSE 5000

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV FLASK_APP=shhh
COPY shhh shhh
