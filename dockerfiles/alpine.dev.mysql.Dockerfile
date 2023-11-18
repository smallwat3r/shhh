# This dockerfile runs the application with the bare Flask
# server. As it's for development only purposes.
#
# When using Gunicorn in a more prod-like config, multiple
# workers would require to use the --preload option, else
# the scheduler would spawn multiple scheduler instances.
#
# Note it would not be comptatible with Gunicorn --reload
# flag, which is useful to reload the app on change, for
# development purposes.
#
# Example: CMD gunicorn -b :8081 -w 3 wsgi:app --preload
#
# To use Gunicorn, please use: alpine.gunicorn.Dockerfile

FROM python:3.12-alpine3.18

RUN apk update \
  && apk add --no-cache \
    gcc \
    g++ \
    libffi-dev \
    musl-dev \
    mariadb-dev \
    yarn \
  && python -m pip install --upgrade pip

ENV TZ UTC

WORKDIR /opt/shhh

ARG GROUP=app USER=shhh UID=1001 GID=1001

RUN addgroup --gid "$GID" "$GROUP" \
    && adduser --uid "$UID" --disabled-password --gecos "" \
        --ingroup "$GROUP" "$USER"

USER $USER
ENV PATH="/home/$USER/.local/bin:${PATH}"

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

COPY requirements.mysql.txt .
RUN pip install --no-cache-dir --no-warn-script-location \
    --user -r requirements.mysql.txt

COPY --chown=$USER:$GROUP . .

RUN yarn install --modules-folder=shhh/static/vendor

CMD flask run --host=0.0.0.0 --port 8081 --reload
