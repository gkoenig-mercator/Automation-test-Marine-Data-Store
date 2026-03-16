import os

import dotenv
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
        print("response:", response.json())
        return response.json().get("access_token", "")


if __name__ == "__main__":
    authentificator = Authentificator(
        username=os.getenv("EDITO_USERNAME"),
        password=os.getenv("EDITO_PASSWORD"),
        client_id=os.getenv("EDITO_CLIENT_ID"),
    )
    token = authentificator.get_token()
    print("Access Token:", token)
