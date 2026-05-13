import logging
import os


class CustomFormatter(logging.Formatter):
    _format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def format(self, record):
        formatter = logging.Formatter(self._format, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


if os.getenv("PYTHON_LOG_DEBUG"):
    level = logging.DEBUG
else:
    level = logging.INFO

logging.getLogger().setLevel(level)
logHandler = logging.StreamHandler()
logHandler.setLevel(level)
logHandler.setFormatter(CustomFormatter())

logger = logging.getLogger("catalogue_check")
logger.addHandler(logHandler)

logging.getLogger("copernicusmarine").setLevel("INFO")
