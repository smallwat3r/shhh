FROM python:3.8.2-alpine3.11

RUN apk update \
  && apk add --no-cache \
    gcc \
    libffi-dev \
    musl-dev \
    postgresql-dev \
    yarn

WORKDIR /opt/shhh

RUN addgroup -g 12001 app \
  && adduser -u 12001 --disabled-password --gecos "" --ingroup app app

USER app

ENV PATH="/home/app/.local/bin:${PATH}"

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt \
  && find /home/app/.local \
    \( -type d -a -name test -o -name tests \) \
    -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
    -exec rm -rf '{}' +

COPY --chown=app:app . .

RUN yarn install --modules-folder=shhh/static/vendor
CMD gunicorn -b :5000 -w 3 wsgi:app --preload
