import os

import dotenv

from deploy.auth import Authenticator
from deploy.client import EditoClient
from deploy.urls import MY_SERVICES_URL

dotenv.load_dotenv()


def _get_service_info(client: EditoClient | None = None) -> dict:
    if client is None:
        authentificator = Authenticator(client_id="onyxia")
        token = authentificator.get_token()
        client = EditoClient(token=token, project=os.getenv("EDITO_PROJECT"))
    response = client.get(url=MY_SERVICES_URL)
    response.raise_for_status()
    return response.json()


def get_postgres_url(client: EditoClient | None = None) -> str:
    infos = [
        app
        for app in _get_service_info(client).get("apps", [])
        if "postgresql" in app.get("name", "").lower()
    ]
    if not infos:
        raise ValueError("No PostgreSQL service found in the services info.")
    info = infos[0]
    # TODO: ask to have more info: port and host
    username = info["env"]["postgresql.auth.username"]
    password = info["env"]["postgresql.auth.password"]
    database_host = f"{info['id']}.{username}"
    database_port = 5432
    database_name = info["env"]["postgresql.auth.database"]
    return f"postgresql+psycopg2://{username}:{password}@{database_host}:{database_port}/{database_name}"
