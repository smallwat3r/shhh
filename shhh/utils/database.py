import os

import pymysql

from .. import app, ROOT_PATH


class DbConn:
    """Manage database."""

    __slots__ = ("cnx", "cur", "path_temp")

    def __init__(self, path_temp=ROOT_PATH):
        self.cnx = pymysql.connect(charset="utf8",
                                   **app.config["DB_CREDENTIALS"])
        self.cur = self.cnx.cursor()
        self.path_temp = os.path.join(path_temp, "sql")

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.cur.close()

    def close(self):
        """Close DB connection."""
        self.cur.close()

    @staticmethod
    def _render_template(filepath):
        """Return SQL content from file."""
        with open(filepath) as f:
            return f.read()

    def get(self, query, args=None):
        """Return SQL results in a dict format."""

        def _return_null_format_by_type(value):
            """Return correct value from value type."""
            if isinstance(value, int):
                return 0
            if isinstance(value, float):
                return 0.0
            return ""

        self.cur.execute(
            self._render_template(os.path.join(self.path_temp, query)), args)
        r = [
            dict((self.cur.description[i][0],
                  value if value else _return_null_format_by_type(value),
                  ) for i,
                 value in enumerate(row)) for row in self.cur.fetchall()
        ]
        return r if r else None

    def commit(self, query, args=None):
        """Commit SQL request."""
        self.cur.execute(
            self._render_template(os.path.join(self.path_temp, query)), args)
        self.cnx.commit()
