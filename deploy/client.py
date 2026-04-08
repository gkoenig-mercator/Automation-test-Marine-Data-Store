import requests


class EditoClient:
    """
    Requests client with authentified calls through bearer token.
    """

    def __init__(self, token: str, project: str | None = None) -> None:
        self.token = token
        self.project = project

    def _headers(self, include_project: bool = True) -> dict:
        headers = {"Authorization": f"Bearer {self.token}"}
        if include_project and self.project:
            headers["ONYXIA-PROJECT"] = self.project
        return headers

    def put(self, url: str, payload: dict) -> requests.Response:
        response = requests.put(url, json=payload, headers=self._headers())
        response.raise_for_status()
        return response

    def post(
        self, url: str, payload: dict, include_project: bool = False
    ) -> requests.Response:
        response = requests.post(
            url, json=payload, headers=self._headers(include_project=include_project)
        )
        response.raise_for_status()
        return response

    def delete(self, url: str, params: dict | None = None) -> requests.Response:
        response = requests.delete(url, headers=self._headers(), params=params)
        response.raise_for_status()
        return response
