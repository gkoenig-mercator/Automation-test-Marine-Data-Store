import argparse
import os

import json5
from dotenv import load_dotenv

from deploy.auth import Authenticator
from deploy.client import EditoClient
from deploy.urls import PROCESS_NAME, process_execution_url
from deploy.utils import get_postgres_url

load_dotenv()

COPERNICUSMARINE_SERVICE_USERNAME = os.getenv("COPERNICUSMARINE_SERVICE_USERNAME")
COPERNICUSMARINE_SERVICE_PASSWORD = os.getenv("COPERNICUSMARINE_SERVICE_PASSWORD")
MAXIMUM_DATASETS_TO_VALIDATE = os.getenv("MAXIMUM_DATASETS_TO_VALIDATE")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
REPORT_RECIPIENT_EMAIL_ADDRESS = os.getenv("REPORT_RECIPIENT_EMAIL_ADDRESS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start an EDITO process execution.")
    parser.add_argument(
        "--version", default=None, help="Process version (default: None)"
    )
    args = parser.parse_args()
    # TODO: contact EDITO team to have a "latest" or default version
    if not args.version:
        raise ValueError(
            "Version is required. Use --version to specify it "
            "or as an env variable if you are using a Make command."
        )
    authentificator = Authenticator(client_id="onyxia")
    token = authentificator.get_token()

    url = process_execution_url(process_id=PROCESS_NAME, version=args.version)
    client = EditoClient(token=token, project=os.getenv("EDITO_PROJECT"))

    payload = json5.load(open("deploy/process/start_process_payload.json5"))
    if not COPERNICUSMARINE_SERVICE_USERNAME or not COPERNICUSMARINE_SERVICE_PASSWORD:
        raise ValueError(
            "COPERNICUSMARINE_SERVICE_USERNAME and COPERNICUSMARINE_SERVICE_PASSWORD "
            "environment variables must be set."
        )
    inputs = {
        "DATABASE_URL": get_postgres_url(client),
        "COPERNICUSMARINE_SERVICE_USERNAME": COPERNICUSMARINE_SERVICE_USERNAME,
        "COPERNICUSMARINE_SERVICE_PASSWORD": COPERNICUSMARINE_SERVICE_PASSWORD,
    }
    if EMAIL_PASSWORD:
        inputs["EMAIL_PASSWORD"] = EMAIL_PASSWORD
    if REPORT_RECIPIENT_EMAIL_ADDRESS:
        inputs["REPORT_RECIPIENT_EMAIL_ADDRESS"] = REPORT_RECIPIENT_EMAIL_ADDRESS
    if MAXIMUM_DATASETS_TO_VALIDATE:
        inputs["MAXIMUM_DATASETS_TO_VALIDATE"] = MAXIMUM_DATASETS_TO_VALIDATE
    payload["processInputs"]["inputs"] = inputs
    response = client.post(url=url, payload=payload)
    print("Process started successfully:", response.json())
