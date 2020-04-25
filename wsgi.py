import os

from shhh.app import create_app

app = create_app(os.environ.get("FLASK_ENV"))

if __name__ == "__main__":
    app.run()
