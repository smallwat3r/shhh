from flask_restful import fields

HELP_CREATE = {
    "secret":
        "Secret message to encrypt.",
    "passphrase":
        "Passphrase to encrypt secret, min 5 chars, 1 number, 1 uppercase.",
    "days":
        "Number of days to keep alive (needs to be an integer)."
}

HELP_READ = {
    "slug": "Secret slug id.",
    "passphrase": "Passphrase shared to decrypt message."
}

FIELDS_CREATE = {
    "status": fields.String,
    "details": fields.String,
    "slug": fields.String,
    "link": fields.String,
    "expires_on": fields.String
}

FIELDS_READ = {"status": fields.String, "msg": fields.String}
