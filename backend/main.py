
import json
import time
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError

from backend.engine.stub import stub_result
from backend.schemas import (
    ControlMessage,
    LandmarkMessage,
    SessionResult,
    incoming_adapter,
)

app = FastAPI(title="MoveWell AI backend")

# Development only: allow HTTP pages served from localhost on any port.
# Pages opened with file:// have a null origin and are not allowed.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# In-memory storage. Replace with SQLite during integration.
sessions: dict[str, dict] = {}


class SessionCreated(BaseModel):
    session_id: str
    started_at: datetime


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


def active_elapsed_ms(session: dict) -> float:
    """Calculate server-measured active elapsed time, excluding pauses."""
    now = time.monotonic()

    elapsed = now - session["started_monotonic"]
    elapsed -= session["paused_total_s"]

    if session["paused"]:
        elapsed -= now - session["pause_started_monotonic"]

    return max(0.0, elapsed * 1000.0)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/sessions", response_model=SessionCreated)
def create_session():
    session_id = f"demo-{uuid.uuid4().hex[:8]}"
    started_at = utc_now()

    sessions[session_id] = {
        "started_at": started_at,
        "started_monotonic": time.monotonic(),
        "paused": False,
        "pause_started_monotonic": None,
        "paused_total_s": 0.0,
        "ended": False,
        "result": SessionResult(
            session_id=session_id,
            started_at=started_at,
        ),
    }

    return SessionCreated(
        session_id=session_id,
        started_at=started_at,
    )


@app.websocket("/ws/sessions/{session_id}")
async def session_socket(websocket: WebSocket, session_id: str):
    # Accept first so clients can receive application-specific close codes.
    await websocket.accept()

    session = sessions.get(session_id)

    if session is None:
        await websocket.close(code=4404, reason="unknown session")
        return

    if session["ended"]:
        await websocket.close(code=4409, reason="session already ended")
        return

    try:
        while True:
            raw = await websocket.receive_text()

            # The session may have ended through the HTTP endpoint.
            if session["ended"]:
                await websocket.close(
                    code=4409,
                    reason="session already ended",
                )
                return

            try:
                msg = incoming_adapter.validate_json(raw)
            except ValidationError as exc:
                await websocket.send_json({
                    "error": "invalid_message",
                    "detail": json.loads(
                        exc.json(include_url=False)
                    ),
                })
                continue

            if isinstance(msg, ControlMessage):
                if msg.action == "pause" and not session["paused"]:
                    session["paused"] = True
                    session["pause_started_monotonic"] = time.monotonic()

                elif msg.action == "resume" and session["paused"]:
                    now = time.monotonic()
                    session["paused_total_s"] += (
                        now - session["pause_started_monotonic"]
                    )
                    session["pause_started_monotonic"] = None
                    session["paused"] = False

                elif msg.action == "calibrate":
                    # Calibration will be implemented in the real engine.
                    pass

            elif isinstance(msg, LandmarkMessage):
                if not session["paused"]:
                    # DEMO ONLY: validate landmarks, but do not analyze them.
                    # The stub uses server active time, not msg.t.
                    elapsed_ms = active_elapsed_ms(session)

                    session["result"] = stub_result(
                        session_id,
                        session["started_at"],
                        elapsed_ms,
                    )

            await websocket.send_text(
                session["result"].model_dump_json()
            )

    except WebSocketDisconnect:
        pass


@app.post("/sessions/{session_id}/end", response_model=SessionResult)
def end_session(session_id: str):
    session = sessions.get(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="unknown session",
        )

    if not session["ended"]:
        # Account for any pause still in progress.
        if session["paused"]:
            now = time.monotonic()
            session["paused_total_s"] += (
                now - session["pause_started_monotonic"]
            )
            session["pause_started_monotonic"] = None
            session["paused"] = False

        session["ended"] = True

        session["result"] = session["result"].model_copy(
            update={"ended_at": utc_now()}
        )

    return session["result"]


@app.get("/sessions", response_model=list[SessionResult])
def list_sessions():
    return [
        session["result"]
        for session in sessions.values()
    ]


@app.get("/sessions/{session_id}", response_model=SessionResult)
def get_session(session_id: str):
    session = sessions.get(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="unknown session",
        )

    return session["result"]
