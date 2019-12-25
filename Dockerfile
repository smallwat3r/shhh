# -*- coding: utf-8 -*-
# File  : Dockerfile
# Date  : 18.09.2019
# Author: Austin Schaffer <schaffer.austin.t@gmail.com>

FROM alpine:3.8

RUN apk update && \
    apk add build-base python3 python3-dev libffi-dev libressl-dev && \
    cd /usr/local/bin && \
    ln -s /usr/bin/python3 python && \
    pip3 install --upgrade pip

EXPOSE 5000

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV FLASK_APP=shhh
COPY shhh shhh

CMD [ "python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000" ]
