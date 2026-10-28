# schema v0.1
from datetime import datetime
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, TypeAdapter

SchemaVersion = Literal["0.1"]
SCHEMA_VERSION: SchemaVersion = "0.1"
NUM_LANDMARKS = 33  # MediaPipe pose landmarks

Phase = Literal["bent", "extending", "held", "returning", "unknown"]
TrackingStatus = Literal["good", "limited", "unable_to_assess"]


# ---------- Input: what the browser sends to the backend ----------

class Landmark(BaseModel):
    x: float  # normalized; can fall slightly outside 0-1 when off-frame
    y: float
    z: float = 0.0
    visibility: float = Field(default=0.0, ge=0.0, le=1.0)


class LandmarkMessage(BaseModel):
    type: Literal["landmarks"]
    # elapsed milliseconds since the browser session started
    t: float = Field(ge=0.0)
    landmarks: list[Landmark] = Field(
        min_length=NUM_LANDMARKS, max_length=NUM_LANDMARKS
    )


class ControlMessage(BaseModel):
    type: Literal["control"]
    action: Literal["pause", "resume", "calibrate"]


# main.py uses this to validate every incoming WebSocket message
IncomingMessage = Annotated[
    Union[LandmarkMessage, ControlMessage], Field(discriminator="type")
]
incoming_adapter = TypeAdapter(IncomingMessage)


# ---------- Output: what the backend returns ----------

class Exercise(BaseModel):
    name: str = "seated_knee_extension"
    source_url: str = "https://www.leedsth.nhs.uk/patients/resources/knee-exercises/"
    config_version: str = "0.1"


class Metrics(BaseModel):
    knee_angle_deg: float | None = None
    hold_elapsed_s: float | None = Field(default=None, ge=0.0)


class Flag(BaseModel):
    rule_id: str
    timestamp: datetime
    reason: str  # plain words, no diagnosis
    confidence: float = Field(ge=0.0, le=1.0)


class SessionResult(BaseModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    session_id: str
    exercise: Exercise = Field(default_factory=Exercise)
    started_at: datetime
    ended_at: datetime | None = None
    rep_count: int = Field(default=0, ge=0)       # completed reps only
    attempted_reps: int = Field(default=0, ge=0)  # started but not completed
    phase: Phase = "unknown"
    tracking_status: TrackingStatus = "unable_to_assess"
    missing_landmarks: list[str] = Field(default_factory=list)
    metrics: Metrics = Field(default_factory=Metrics)
    flags: list[Flag] = Field(default_factory=list)
