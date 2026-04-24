import os

from dotenv import load_dotenv

load_dotenv()

_ENV_VARS = {"DATABASE_URL", "COPERNICUSMARINE_USERNAME", "COPERNICUSMARINE_PASSWORD"}


def __getattr__(name: str) -> str:
    if name in _ENV_VARS:
        value = os.getenv(name, "")
        if not value:
            raise ValueError(f"{name} environment variable is not set.")
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
