import os

from shhh.entrypoint import create_app

app = create_app(os.environ.get("FLASK_ENV"))

if __name__ == "__main__":
    app.run()
