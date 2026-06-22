import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Database configuration
    DB_PROTOCOL: str = os.getenv("DB_PROTOCOL", "mongodb")
    DB_HOST: str = os.getenv("DB_HOST", "localhost:27017")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASS: str = os.getenv("DB_PASS", "")
    DB_NAME: str = os.getenv("DB_NAME", "habits_db")

    # CORS configuration
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173")

    @classmethod
    def get_cors_origins_list(cls) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in cls.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
