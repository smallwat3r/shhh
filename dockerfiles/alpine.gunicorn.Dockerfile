# Dockerfile using Gunicorn and non-root user

FROM python:3.12-alpine3.18

RUN apk add --no-cache \
      gcc g++ musl-dev libffi-dev openssl-dev postgresql-dev \
      nodejs yarn && \
    python -m pip install --upgrade pip

ENV TZ=UTC

WORKDIR /opt/shhh

ARG GROUP=app USER=shhh UID=1001 GID=1001
RUN addgroup --gid "$GID" "$GROUP" \
 && adduser --uid "$UID" --disabled-password --gecos "" --ingroup "$GROUP" "$USER"

RUN chown -R "$USER:$GROUP" /opt/shhh
RUN python -m venv /opt/venv && chown -R "$USER:$GROUP" /opt/venv

USER $USER
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
ENV PATH="/opt/venv/bin:${PATH}"

COPY --chown=$USER:$GROUP requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

COPY --chown=$USER:$GROUP wsgi.py .
COPY --chown=$USER:$GROUP shhh ./shhh
COPY --chown=$USER:$GROUP package.json .

RUN mkdir -p /opt/shhh/shhh/static/vendor \
 && yarn install --modules-folder=/opt/shhh/shhh/static/vendor

RUN python -m flask --version
CMD ["gunicorn", "-b", ":8081", "-w", "3", "wsgi:app", "--preload"]
