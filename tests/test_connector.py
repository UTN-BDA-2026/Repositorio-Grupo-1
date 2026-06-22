import os
import unittest
from unittest.mock import patch

from app.database.connector import MongoConnector


class ConnectorTests(unittest.TestCase):
    # Valida construcción de URI según variables de entorno.
    def setUp(self):
        MongoConnector._client = None
        MongoConnector._database = None

    def test_build_uri_requires_db_host(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                MongoConnector._build_uri()

    def test_build_uri_with_credentials_and_protocol(self):
        with patch.dict(
            os.environ,
            {
                "DB_USER": "user",
                "DB_PASS": "pass",
                "DB_HOST": "cluster.mongodb.net",
                "DB_NAME": "habits_db",
                "DB_PROTOCOL": "mongodb+srv",
            },
            clear=True,
        ):
            uri, db_name = MongoConnector._build_uri()
            self.assertEqual(db_name, "habits_db")
            self.assertIn("user:pass@cluster.mongodb.net/habits_db", uri)

    def test_build_uri_encodes_password_special_chars(self):
        with patch.dict(
            os.environ,
            {
                "DB_USER": "user",
                "DB_PASS": "p@ss word",
                "DB_HOST": "cluster.mongodb.net",
                "DB_NAME": "habits_db",
            },
            clear=True,
        ):
            uri, _ = MongoConnector._build_uri()
            self.assertIn("user:p%40ss+word@cluster.mongodb.net", uri)


if __name__ == "__main__":
    unittest.main()
