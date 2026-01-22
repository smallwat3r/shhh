# Dockerfile using Gunicorn, multi-stage build, and non-root user

# Stage 1: Builder
FROM python:3.12-alpine3.21 AS builder

RUN apk add --no-cache \
      gcc g++ musl-dev libffi-dev openssl-dev postgresql-dev \
      nodejs yarn

WORKDIR /opt/shhh

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

COPY package.json .
RUN mkdir -p /opt/shhh/shhh/static/vendor \
 && yarn install --modules-folder=/opt/shhh/shhh/static/vendor

# Stage 2: Runtime
FROM python:3.12-alpine3.21

RUN apk add --no-cache libpq

ENV TZ=UTC
WORKDIR /opt/shhh

ARG GROUP=app USER=shhh UID=1001 GID=1001
RUN addgroup --gid "$GID" "$GROUP" \
 && adduser --uid "$UID" --disabled-password --gecos "" --ingroup "$GROUP" "$USER"

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /opt/shhh/shhh/static/vendor /opt/shhh/shhh/static/vendor

COPY wsgi.py .
COPY shhh ./shhh

RUN chown -R "$USER:$GROUP" /opt/shhh /opt/venv

USER $USER
ENV PATH="/opt/venv/bin:${PATH}"

EXPOSE 8081

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:8081/ || exit 1

CMD ["gunicorn", "-b", ":8081", "-w", "3", "wsgi:app", "--preload"]
