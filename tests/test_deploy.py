import responses

from deploy.auth import Authenticator
from deploy.client import EditoClient
from deploy.urls import AUTH_URL, DATALAB_API_URL, process_execution_url


def test_process_execution_url():
    url = process_execution_url(process_id="my-proc", version="1.2.3")
    assert (
        url
        == "https://api.dive.edito.eu/processes/processes/process-playground-my-proc-1.2.3/execution"
    )


@responses.activate
def test_authentificator_get_token():
    responses.post(AUTH_URL, json={"access_token": "fake-token"}, status=200)
    auth = Authenticator(username="user", password="pass", client_id="client")
    token = auth.get_token()
    assert token == "fake-token"
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == AUTH_URL


@responses.activate
def test_client_put():
    responses.put(DATALAB_API_URL, json={"status": "ok"}, status=200)
    client = EditoClient(token="test-token", project="my-project")
    resp = client.put(url=DATALAB_API_URL, payload={"key": "value"})
    assert resp.status_code == 200
    assert len(responses.calls) == 1
    assert responses.calls[0].request.headers["Authorization"] == "Bearer test-token"
    assert responses.calls[0].request.headers["ONYXIA-PROJECT"] == "my-project"


@responses.activate
def test_client_post():
    url = process_execution_url(process_id="test", version="0.0.1")
    responses.post(url, json={"status": "started"}, status=200)
    client = EditoClient(token="test-token", project="my-project")
    resp = client.post(url=url, payload={"input": "data"})
    assert resp.status_code == 200
    assert len(responses.calls) == 1
    assert responses.calls[0].request.headers["Authorization"] == "Bearer test-token"
    # post without include_project should NOT send ONYXIA-PROJECT
    assert "ONYXIA-PROJECT" not in responses.calls[0].request.headers


@responses.activate
def test_client_delete():
    responses.delete(DATALAB_API_URL, json={"status": "deleted"}, status=200)
    client = EditoClient(token="test-token", project="my-project")
    resp = client.delete(url=DATALAB_API_URL, params={"path": "my-process"})
    assert resp.status_code == 200
    assert len(responses.calls) == 1
    assert responses.calls[0].request.headers["Authorization"] == "Bearer test-token"
