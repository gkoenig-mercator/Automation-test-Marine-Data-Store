import os
from urllib import response

import dotenv
import json5
import requests

dotenv.load_dotenv()


class Authentificator:
    def __init__(
        self, username: str | None, password: str | None, client_id: str | None
    ) -> None:
        if not username:
            username = os.getenv("EDITO_USERNAME")
        if not password:
            password = os.getenv("EDITO_PASSWORD")
        if not client_id:
            client_id = os.getenv("EDITO_CLIENT_ID")

        if not username or not password or not client_id:
            raise ValueError(
                "Username, password, and client_id must be provided either as arguments or environment variables."
            )
        self.username = username
        self.password = password
        self.client_id = client_id
        self.url = "https://auth.dive.edito.eu/auth/realms/datalab/protocol/openid-connect/token"

    def get_token(self) -> str:
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "username": self.username,
            "password": self.password,
            "scope": "openid",
        }
        response = requests.post(self.url, data=data)
        response.raise_for_status()
        return response.json().get("access_token", "")


class Client:
    """
    Requests client with
    authentified calls through bearer token.
    """

    def __init__(self, token: str, url: str, project: str | None) -> None:
        self.token = token
        self.url = url
        self.project = project

    def start_process(self, payload: dict) -> requests.Response:
        headers = {"Authorization": f"Bearer {self.token}"}
        if self.project:
            headers["ONYXIA-PROJECT"] = self.project
        response = requests.put(self.url, json=payload, headers=headers)
        print("Response status code:", response)
        response.raise_for_status()
        return response


if __name__ == "__main__":
    authentificator = Authentificator(
        username=os.getenv("EDITO_USERNAME"),
        password=os.getenv("EDITO_PASSWORD"),
        client_id="onyxia",
    )

    token = authentificator.get_token()
    url = "https://datalab.dive.edito.eu/api/my-lab/app"
    client = Client(
        token=token,
        url=url,
        project=os.getenv("EDITO_PROJECT"),
    )
    payload = json5.load(open("deploy/process/add_process_payload.json5"))
    response = client.start_process(payload=payload)
    print("Process started successfully:", response.json())
