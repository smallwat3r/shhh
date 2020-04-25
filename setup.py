import setuptools

setuptools.setup(
    name="shhh",
    version="0.0.1",
    packages=setuptools.find_packages(),
    requirements=[
        "flask",
        "psycopg2",
        "Flask-APScheduler",
        "requests",
        "flask_restful",
        "flask_sqlalchemy",
        "webargs",
        "cryptography"
    ])
