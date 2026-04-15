import argparse
import os

import json5

from deploy.auth import Authenticator
from deploy.client import EditoClient
from deploy.urls import PROCESS_NAME, process_execution_url

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
    response = client.post(url=url, payload=payload)
    print("Process started successfully:", response.json())
