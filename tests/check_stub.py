from datetime import datetime, timedelta

from backend.engine.stub import stub_result

started = datetime.now()

def at(t_ms):
    return stub_result("demo-001", started, t_ms)


# 1. Phases and angles in a full (complete) cycle
r = at(0)
assert (r.phase, r.metrics.knee_angle_deg) == ("bent", 90.0)

r = at(3000)
assert (r.phase, r.metrics.knee_angle_deg) == ("extending", 130.0)

r = at(6000)
assert (r.phase, r.metrics.knee_angle_deg) == ("held", 170.0)
assert r.metrics.hold_elapsed_s == 2.0

r = at(10000)
assert (r.phase, r.metrics.knee_angle_deg) == ("returning", 130.0)
assert r.metrics.hold_elapsed_s is None

r = at(11500)
assert (r.phase, r.metrics.knee_angle_deg) == ("bent", 90.0)
print("1 OK: full-cycle phases and angles")

# 2. Rep counts
r = at(30000)
assert (r.rep_count, r.attempted_reps, len(r.flags)) == (2, 0, 0)

r = at(40000)
assert (r.rep_count, r.attempted_reps, len(r.flags)) == (3, 0, 0)

r = at(50000)
assert (r.rep_count, r.attempted_reps, len(r.flags)) == (3, 1, 1)
print("2 OK: rep and attempted-rep counts")

# 3. The incomplete (4th) cycle never holds
r = at(39000)
assert (r.phase, r.metrics.knee_angle_deg) == ("extending", 110.0)
assert r.metrics.hold_elapsed_s is None
print("3 OK: incomplete cycle has no hold")

# 4. The flag matches the simulated movement
flag = at(50000).flags[0]
assert flag.rule_id == "incomplete_rep"
assert flag.timestamp == started + timedelta(seconds=40)
print("4 OK: flag rule and timestamp")

# 5. Demo prefix on the session id
assert stub_result("abc", started, 0).session_id == "demo-abc"
assert stub_result("demo-001", started, 0).session_id == "demo-001"
print("5 OK: demo- prefix")

# 6. Negative time is rejected
try:
    at(-1)
    raise AssertionError("negative time was accepted")
except ValueError:
    print("6 OK: negative time rejected")

# 7. Counts never go down, and every result is valid, over a long run
last_reps = 0
last_attempted = 0
for t_ms in range(0, 200_000, 500):
    r = at(t_ms)
    assert r.rep_count >= last_reps
    assert r.attempted_reps >= last_attempted
    last_reps, last_attempted = r.rep_count, r.attempted_reps
print("7 OK: counts never decrease over 200 seconds")

print("All stub checks passed")