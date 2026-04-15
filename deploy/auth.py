import os

import dotenv
import requests

from deploy.urls import AUTH_URL

dotenv.load_dotenv()


class Authenticator:
    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        client_id: str | None = None,
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

    def get_token(self) -> str:
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "username": self.username,
            "password": self.password,
            "scope": "openid",
        }
        response = requests.post(AUTH_URL, data=data)
        response.raise_for_status()
        return response.json().get("access_token", "")
