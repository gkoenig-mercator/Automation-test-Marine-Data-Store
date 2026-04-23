import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

COPERNICUSMARINE_USERNAME = os.getenv("COPERNICUSMARINE_USERNAME", "")
if not COPERNICUSMARINE_USERNAME:
    raise ValueError("COPERNICUSMARINE_USERNAME environment variable is not set.")
COPERNICUSMARINE_PASSWORD = os.getenv("COPERNICUSMARINE_PASSWORD", "")
if not COPERNICUSMARINE_PASSWORD:
    raise ValueError("COPERNICUSMARINE_PASSWORD environment variable is not set.")
