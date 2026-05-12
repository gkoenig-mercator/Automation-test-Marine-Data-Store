import logging
import os


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    _format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + _format + reset,
        logging.INFO: grey + _format + reset,
        logging.WARNING: yellow + _format + reset,
        logging.ERROR: red + _format + reset,
        logging.CRITICAL: bold_red + _format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


if os.getenv("PYTHON_LOG_DEBUG"):
    level = logging.DEBUG
else:
    level = logging.INFO

logging.getLogger().setLevel(level)
logHandler = logging.StreamHandler()
logHandler.setLevel(level)
logHandler.setFormatter(CustomFormatter())

logger = logging.getLogger("logger")
logger.addHandler(logHandler)

logging.getLogger("copernicusmarine").setLevel("INFO")
