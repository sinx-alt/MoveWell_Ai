INSERT OR REPLACE INTO sessions
(session_id, schema_version, exercise_name, config_version, started_at, ended_at, rep_count, attempted_reps)
VALUES
('demo-001', '0.1', 'seated_knee_extension', '0.1', '2026-10-25T10:00:00', '2026-10-25T10:08:00', 10, 1),
('demo-002', '0.1', 'seated_knee_extension', '0.1', '2026-10-26T09:30:00', '2026-10-26T09:38:00', 7, 3),
('demo-003', '0.1', 'seated_knee_extension', '0.1', '2026-10-27T18:15:00', '2026-10-27T18:22:00', 9, 2),
('demo-004', '0.1', 'seated_knee_extension', '0.1', '2026-10-28T08:45:00', '2026-10-28T08:52:00', 10, 0);

INSERT OR REPLACE INTO flags (id, session_id, rule_id, timestamp, reason, confidence)
VALUES
(1001, 'demo-001', 'hold_too_short', '2026-10-25T10:00:41', 'Leg was lowered before the hold time finished', 0.7),
(1002, 'demo-002', 'hold_too_short', '2026-10-26T09:31:10', 'Leg was lowered before the hold time finished', 0.7),
(1003, 'demo-002', 'movement_too_fast', '2026-10-26T09:33:25', 'Leg was moved faster than the configured pace', 0.6),
(1004, 'demo-003', 'tracking_lost', '2026-10-27T18:17:05', 'Leg was not fully visible, so this part could not be assessed', 0.9);