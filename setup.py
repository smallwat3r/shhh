import setuptools

setuptools.setup(
    name="shhh",
    version="0.0.1",
    packages=setuptools.find_packages(),
    requirements=[
        "flask",
        "psycopg2",
        "celery",
        "requests",
        "flask_restful",
        "flask_sqlalchemy",
        "redis",
        "webargs",
        "cryptography"
    ])
