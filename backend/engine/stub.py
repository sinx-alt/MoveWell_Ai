
from datetime import datetime, timedelta

from backend.schemas import Flag, Metrics, SessionResult

CYCLE_S = 12.0
ABORT_EVERY = 4  # Every 4th cycle is an incomplete repetition


def stub_result(
    session_id: str,
    started_at: datetime,
    t_ms: float,
) -> SessionResult:
    """Generate simulated exercise data for demos and UI testing only."""

    if t_ms < 0:
        raise ValueError("t_ms must be non-negative")

    # Clearly identify simulated sessions.
    sid = (
        session_id
        if session_id.startswith("demo-")
        else f"demo-{session_id}"
    )

    t = t_ms / 1000.0
    idx = int(t // CYCLE_S)
    pos = t % CYCLE_S

    # Count only cycles that have fully finished.
    aborted_done = sum(
        1
        for i in range(idx)
        if i % ABORT_EVERY == ABORT_EVERY - 1
    )

    rep_count = idx - aborted_done
    attempted_reps = aborted_done

    # Determine whether the current cycle is simulated as aborted.
    is_aborted = idx % ABORT_EVERY == ABORT_EVERY - 1

    hold_elapsed_s = None

    if is_aborted:
        # Incomplete repetition: extends halfway, then returns.
        if pos < 2:
            phase, angle = "bent", 90.0

        elif pos < 4:
            phase = "extending"
            angle = 90.0 + (pos - 2) / 2 * 40.0

        elif pos < 6:
            phase = "returning"
            angle = 130.0 - (pos - 4) / 2 * 40.0

        else:
            phase, angle = "bent", 90.0

    else:
        # Complete simulated repetition with a 5-second hold.
        if pos < 2:
            phase, angle = "bent", 90.0

        elif pos < 4:
            phase = "extending"
            angle = 90.0 + (pos - 2) / 2 * 80.0

        elif pos < 9:
            phase, angle = "held", 170.0
            hold_elapsed_s = pos - 4

        elif pos < 11:
            phase = "returning"
            angle = 170.0 - (pos - 9) / 2 * 80.0

        else:
            phase, angle = "bent", 90.0

    # Add one demo flag for each fully completed aborted cycle.
    flags = [
        Flag(
            rule_id="incomplete_rep",
            timestamp=started_at
            + timedelta(seconds=i * CYCLE_S + 4),
            reason="Leg began returning before the hold started (demo data)",
            confidence=0.7,
        )
        for i in range(idx)
        if i % ABORT_EVERY == ABORT_EVERY - 1
    ]

    return SessionResult(
        session_id=sid,
        started_at=started_at,
        rep_count=rep_count,
        attempted_reps=attempted_reps,
        phase=phase,
        tracking_status="good",
        metrics=Metrics(
            knee_angle_deg=round(angle, 1),
            hold_elapsed_s=hold_elapsed_s,
        ),
        flags=flags,
    )
