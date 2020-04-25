from os import environ

from shhh import create_app

app = create_app(environ.get("FLASK_ENV"))

if __name__ == "__main__":
    app.run()
