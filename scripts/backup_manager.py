import argparse
import logging
import os
import subprocess

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def create_backup(archive_path: str) -> None:
    # Usa URI centralizada para exportar la base en un archivo comprimido.
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI environment variable is required")

    args = ["mongodump", "--uri", uri, "--gzip", f"--archive={archive_path}"]
    result = subprocess.run(args, check=True, capture_output=True, text=True)
    if result.stdout:
        LOGGER.info(result.stdout.strip())
    if result.stderr:
        LOGGER.warning(result.stderr.strip())


def restore_backup(archive_path: str) -> None:
    # Restaura el backup y reemplaza datos existentes con `--drop`.
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI environment variable is required")

    args = ["mongorestore", "--uri", uri, "--gzip", f"--archive={archive_path}", "--drop"]
    result = subprocess.run(args, check=True, capture_output=True, text=True)
    if result.stdout:
        LOGGER.info(result.stdout.strip())
    if result.stderr:
        LOGGER.warning(result.stderr.strip())


def parse_args() -> argparse.Namespace:
    # Define interfaz CLI mínima para backup/restore.
    parser = argparse.ArgumentParser(description="MongoDB backup/restore manager")
    parser.add_argument("action", choices=["backup", "restore"])
    parser.add_argument("--archive", default="dump.agz")
    return parser.parse_args()


if __name__ == "__main__":
    # Ejecuta la acción solicitada desde línea de comandos.
    parsed = parse_args()
    if parsed.action == "backup":
        create_backup(parsed.archive)
    else:
        restore_backup(parsed.archive)
