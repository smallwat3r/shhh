from flask_restful import Resource, marshal, reqparse

from .tasks.task_create import create_secret
from .tasks.task_read import read_secret
from .config import (ApiCreateArgs,
                     ApiReadArgs,
                     FIELDS_CREATE,
                     FIELDS_READ,
                     HELP_READ,
                     HELP_CREATE)


class Create(Resource):
    """Create secret API."""

    def __init__(self):
        self.parser = reqparse.RequestParser(bundle_errors=True)
        self.parser.add_argument(ApiCreateArgs.SECRET.value,
                                 type=str,
                                 required=True,
                                 help=HELP_CREATE["secret"])
        self.parser.add_argument(ApiCreateArgs.PASSPHRASE.value,
                                 type=str,
                                 required=True,
                                 help=HELP_CREATE["passphrase"])
        self.parser.add_argument(ApiCreateArgs.DAYS.value,
                                 type=int,
                                 required=True,
                                 help=HELP_CREATE["days"])
        super().__init__()

    def post(self):
        """Process POST request to create secret."""
        args = self.parser.parse_args()
        response = create_secret(args["passphrase"],
                                 args["secret"],
                                 args["days"])
        return {"response": marshal(response, FIELDS_CREATE)}


class Read(Resource):
    """Read secret API."""

    def __init__(self):
        self.parser = reqparse.RequestParser(bundle_errors=True)
        self.parser.add_argument(ApiReadArgs.SLUG.value,
                                 type=str,
                                 required=True,
                                 help=HELP_READ["slug"])
        self.parser.add_argument(ApiReadArgs.PASSPHRASE.value,
                                 type=str,
                                 required=True,
                                 help=HELP_READ["passphrase"])
        super().__init__()

    def get(self):
        """Process GET request to read secret."""
        args = self.parser.parse_args()
        response = read_secret(args["slug"], args["passphrase"])
        return {"response": marshal(response, FIELDS_READ)}
