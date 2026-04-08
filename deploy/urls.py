AUTH_URL = (
    "https://auth.dive.edito.eu/auth/realms/datalab/protocol/openid-connect/token"
)

DATALAB_API_URL = "https://datalab.dive.edito.eu/api/my-lab/app"

PROCESS_API_BASE = "https://api.dive.edito.eu/processes/processes"

PROCESS_NAME = "test-renaud-deploy"


def process_execution_url(process_id: str, version: str) -> str:
    return f"{PROCESS_API_BASE}/process-playground-{process_id}-{version}/execution"
