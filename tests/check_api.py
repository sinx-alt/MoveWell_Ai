from unittest.mock import patch

from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from backend.main import app

client = TestClient(app)
lm = {"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 0.9}


def landmarks(t=0):
    return {"type": "landmarks", "t": t, "landmarks": [lm] * 33}


class FakeClock:
    """Stands in for the time module inside backend.main only."""

    def __init__(self):
        self.now = 1000.0

    def monotonic(self):
        return self.now


clock = FakeClock()

with patch("backend.main.time", clock):
    # 1. health
    assert client.get("/health").json() == {"status": "ok"}
    print("1 OK: health")

    # 2. create a session
    sid = client.post("/sessions").json()["session_id"]
    assert sid.startswith("demo-")
    print("2 OK: session created")

    with client.websocket_connect(f"/ws/sessions/{sid}") as ws:
        # 3. server time decides the result: 6 seconds in is the hold
        clock.now = 1006.0
        ws.send_json(landmarks())
        r = ws.receive_json()
        assert r["phase"] == "held" and r["tracking_status"] == "good"
        print("3 OK: landmarks message gives a result")

        # 4. an invalid message gets an error reply, not a crash
        ws.send_json({"type": "landmarks", "t": 1, "landmarks": [lm] * 32})
        assert ws.receive_json()["error"] == "invalid_message"
        print("4 OK: invalid message rejected")

        # 5. paused time does not count
        ws.send_json({"type": "control", "action": "pause"})
        ws.receive_json()
        clock.now = 1030.0  # 24 seconds pass while paused
        ws.send_json(landmarks())
        r = ws.receive_json()
        assert r["rep_count"] == 0 and r["phase"] == "held"
        ws.send_json({"type": "control", "action": "resume"})
        ws.receive_json()
        clock.now = 1036.0  # 12 active seconds in total
        ws.send_json(landmarks())
        r = ws.receive_json()
        assert r["rep_count"] == 1 and r["phase"] == "bent"
        print("5 OK: pause excludes paused time")

    # 6. end the session and read it back
    final = client.post(f"/sessions/{sid}/end").json()
    assert final["ended_at"] is not None and final["rep_count"] == 1
    assert client.get(f"/sessions/{sid}").status_code == 200
    assert any(s["session_id"] == sid for s in client.get("/sessions").json())
    assert client.get("/sessions/nope").status_code == 404
    print("6 OK: end, get and list")

    # 7. ended and unknown sessions are refused on the WebSocket
    for bad_id in (sid, "nope"):
        try:
            with client.websocket_connect(f"/ws/sessions/{bad_id}") as ws:
                ws.receive_json()
            raise AssertionError(f"{bad_id} was accepted")
        except WebSocketDisconnect:
            pass
    print("7 OK: ended and unknown sessions refused")

# 8. any local port may call the API, other sites may not
ok = client.get("/health", headers={"Origin": "http://localhost:5500"})
assert ok.headers.get("access-control-allow-origin") == "http://localhost:5500"
no = client.get("/health", headers={"Origin": "http://evil.example"})
assert "access-control-allow-origin" not in no.headers
print("8 OK: CORS allows local ports only")

print("All API checks passed")