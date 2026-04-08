import json
import os

from deploy.auth import Authenticator
from deploy.client import EditoClient
from deploy.urls import DATALAB_API_URL

if __name__ == "__main__":
    authentificator = Authenticator()
    token = authentificator.get_token()

    client = EditoClient(token=token, project=os.getenv("EDITO_PROJECT"))
    payload = json.load(open("deploy/database/postgres_payload.json"))
    response = client.put(url=DATALAB_API_URL, payload=payload)
    print("Database started successfully:", response.json())
