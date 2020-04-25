from os import environ

from shhh.app import create_app

app = create_app(environ.get("FLASK_ENV"))

if __name__ == "__main__":
    app.run()
