FROM python:3

EXPOSE 5000

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV FLASK_APP=shhh
COPY shhh shhh

CMD [ "python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000" ]
