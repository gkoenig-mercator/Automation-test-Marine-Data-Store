import argparse
import os

import json5

from deploy.auth import Authenticator
from deploy.client import EditoClient
from deploy.urls import DATALAB_API_URL, PROCESS_NAME

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an EDITO process.")

    parser.add_argument(
        "--version", default=None, help="Process version (default: 0.0.5)"
    )
    parser.add_argument(
        "--code-version",
        default=None,
        help="Version of the code to use or branch name.",
    )
    args = parser.parse_args()
    if not args.version or not args.code_version:
        raise ValueError(
            "Version and code version are required. "
            "Use --version and --code-version to specify them "
            "or as env variables if you are using a Make command."
        )
    authentificator = Authenticator(client_id="onyxia")
    token = authentificator.get_token()

    client = EditoClient(token=token, project=os.getenv("EDITO_PROJECT"))

    # first delete the process if it already exists
    process_name = "add-your-process"
    client.delete(url=DATALAB_API_URL, params={"path": process_name})
    print(f"Process '{process_name}' deleted successfully.")

    # then create the process
    # TODO: check if the version already exists before overwriting; raise in this case
    payload = json5.load(open("deploy/process/add_process_payload.json5"))
    payload["options"]["metadata"]["version"] = args.version
    payload["options"]["metadata"]["id"] = PROCESS_NAME
    payload["options"]["git"]["branch"] = args.code_version
    response = client.put(url=DATALAB_API_URL, payload=payload)
    print("Process added successfully:", response.json())
