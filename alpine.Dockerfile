FROM python:3.10-alpine3.18

RUN apk update \
  && apk add --no-cache \
    gcc \
    g++ \
    libffi-dev \
    musl-dev \
    postgresql-dev \
    yarn \
  && python -m pip install --upgrade pip

ENV TZ UTC

WORKDIR /opt/shhh

ENV GROUP=app USER=shhh UID=12345 GID=23456

RUN addgroup --gid "$GID" "$GROUP" \
    && adduser --uid "$UID" --disabled-password --gecos "" \
        --ingroup "$GROUP" "$USER"

USER "$USER"
ENV PATH="/home/$USER/.local/bin:${PATH}"

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

COPY requirements.txt .
RUN pip install --no-cache-dir --no-warn-script-location \
    --user -r requirements.txt

COPY --chown=$USER:$GROUP . .

RUN yarn install --modules-folder=shhh/static/vendor

# When using Gunicorn in a more prod like config, multiple
# workers would require to use the --preload option, else
# the scheduler would spawn multiple scheduler instances.
# Note it would not be comptatible with Gunicorn --reload
# flag, which is useful to reload the app on change, for
# development purposes.
# Example: CMD gunicorn -b :8080 -w 3 wsgi:app --preload
CMD flask run --host=0.0.0.0 --port 8081 --reload
