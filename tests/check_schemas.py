from datetime import datetime

from pydantic import ValidationError

from backend.schemas import SessionResult, incoming_adapter

# 1. a valid control message
msg = incoming_adapter.validate_json('{"type": "control", "action": "pause"}')
print("1 OK:", msg)

# 2. a valid landmarks message with exactly 33 landmarks
lm = {"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 0.9}
good = {"type": "landmarks", "t": 120.0, "landmarks": [lm] * 33}
print("2 OK:", type(incoming_adapter.validate_python(good)).__name__)

# 3. 32 landmarks must be rejected
bad = {"type": "landmarks", "t": 120.0, "landmarks": [lm] * 32}
try:
    incoming_adapter.validate_python(bad)
    print("3 FAIL: 32 landmarks were accepted")
except ValidationError:
    print("3 OK: 32 landmarks rejected")

# 4. a full result object
result = SessionResult(session_id="demo-001", started_at=datetime.now())
print("4 OK:", result.schema_version, result.rep_count, result.phase)