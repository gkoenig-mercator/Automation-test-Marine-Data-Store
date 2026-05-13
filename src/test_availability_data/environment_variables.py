import os

from dotenv import load_dotenv

from test_availability_data.config.logger import logger

load_dotenv(override=True)

_ENV_VARS = {
    "DATABASE_URL",
    "COPERNICUSMARINE_SERVICE_USERNAME",
    "COPERNICUSMARINE_SERVICE_PASSWORD",
    "EMAIL_PASSWORD",
    "REPORT_RECIPIENT_EMAIL_ADDRESS",
}

_ENV_VARS_THAT_CAN_BE_EMPTY = {
    "EMAIL_PASSWORD",
    "REPORT_RECIPIENT_EMAIL_ADDRESS",
}


def __getattr__(name: str) -> str:
    if name in _ENV_VARS:
        value = os.getenv(name, "").strip().strip("'\"")
        if not value and name not in _ENV_VARS_THAT_CAN_BE_EMPTY:
            raise ValueError(f"{name} environment variable is not set.")
        elif not value:
            logger.warning(f"{name} environment variable is not set, continuing.")
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
