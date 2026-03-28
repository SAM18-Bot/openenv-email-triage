from fastapi.testclient import TestClient

from src.api import app


def test_api_endpoints():
    client = TestClient(app)
    r1 = client.post('/reset', json={"seed": 2})
    assert r1.status_code == 200
    r2 = client.post('/step', json={"action_type": "read", "confidence": 0.7})
    assert r2.status_code == 200
    body = r2.json()
    assert set(body.keys()) == {"observation", "reward", "done", "info"}
    r3 = client.get('/state')
    assert r3.status_code == 200
