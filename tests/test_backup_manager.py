import os
import unittest
from unittest.mock import patch

from scripts.backup_manager import create_backup, restore_backup


class BackupManagerTests(unittest.TestCase):
    # Prueba validaciones y ejecución de comandos de respaldo/restauración mediante subprocess.
    def test_create_backup_requires_uri(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                create_backup("dump.agz")

    @patch("scripts.backup_manager.subprocess.run")
    def test_create_backup_calls_mongodump_with_expected_args(self, run_mock):
        run_mock.return_value.stdout = ""
        run_mock.return_value.stderr = ""
        with patch.dict(os.environ, {"MONGODB_URI": "mongodb://localhost:27017/habits_db"}, clear=True):
            create_backup("dump.agz")
        run_mock.assert_called_once_with(
            ["mongodump", "--uri", "mongodb://localhost:27017/habits_db", "--gzip", "--archive=dump.agz"],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("scripts.backup_manager.subprocess.run")
    def test_restore_backup_calls_mongorestore_with_drop(self, run_mock):
        run_mock.return_value.stdout = ""
        run_mock.return_value.stderr = ""
        with patch.dict(os.environ, {"MONGODB_URI": "mongodb://localhost:27017/habits_db"}, clear=True):
            restore_backup("dump.agz")
        run_mock.assert_called_once_with(
            [
                "mongorestore",
                "--uri",
                "mongodb://localhost:27017/habits_db",
                "--gzip",
                "--archive=dump.agz",
                "--drop",
            ],
            check=True,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
