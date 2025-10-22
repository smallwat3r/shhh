# This Dockerfile starts the application using the basic Flask
# development server. It is intended for development use only,
# not for production.

FROM python:3.12-alpine3.18

RUN apk add --no-cache \
      gcc g++ musl-dev libffi-dev openssl-dev mariadb-dev \
      nodejs yarn && \
    python -m pip install --upgrade pip

ENV TZ=UTC
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

WORKDIR /opt/shhh

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

COPY requirements.mysql.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

COPY wsgi.py .
COPY shhh ./shhh

COPY package.json .
RUN mkdir -p /opt/shhh/shhh/static/vendor \
 && yarn install --modules-folder=/opt/shhh/shhh/static/vendor

RUN python -m flask --version
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port", "8081", "--reload"]
