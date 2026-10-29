package com.movewell.dashboard;

import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

@Controller
public class DashboardController {

    private final List<Map<String, Object>> sessions = List.of(
        Map.of(
            "session_id", "demo-001",
            "exercise_name", "Seated Knee Extension",
            "started_at", "2026-10-25T10:00:00",
            "ended_at", "2026-10-25T10:08:00",
            "rep_count", 10,
            "attempted_reps", 1
        ),
        Map.of(
            "session_id", "demo-002",
            "exercise_name", "Seated Knee Extension",
            "started_at", "2026-10-26T09:30:00",
            "ended_at", "2026-10-26T09:38:00",
            "rep_count", 7,
            "attempted_reps", 3
        ),
        Map.of(
            "session_id", "demo-003",
            "exercise_name", "Seated Knee Extension",
            "started_at", "2026-10-27T18:15:00",
            "ended_at", "2026-10-27T18:22:00",
            "rep_count", 9,
            "attempted_reps", 2
        ),
        Map.of(
            "session_id", "demo-004",
            "exercise_name", "Seated Knee Extension",
            "started_at", "2026-10-28T08:45:00",
            "ended_at", "2026-10-28T08:52:00",
            "rep_count", 10,
            "attempted_reps", 0
        )
    );

    private final List<Map<String, Object>> flags = List.of(
        Map.of(
            "id", 1001,
            "session_id", "demo-001",
            "rule_id", "hold_too_short",
            "timestamp", "2026-10-25T10:00:41",
            "reason", "Leg was lowered before the hold time finished",
            "confidence", 0.7
        ),
        Map.of(
            "id", 1002,
            "session_id", "demo-002",
            "rule_id", "hold_too_short",
            "timestamp", "2026-10-26T09:31:10",
            "reason", "Leg was lowered before the hold time finished",
            "confidence", 0.7
        ),
        Map.of(
            "id", 1003,
            "session_id", "demo-002",
            "rule_id", "movement_too_fast",
            "timestamp", "2026-10-26T09:33:25",
            "reason", "Leg was moved faster than the configured pace",
            "confidence", 0.6
        ),
        Map.of(
            "id", 1004,
            "session_id", "demo-003",
            "rule_id", "tracking_lost",
            "timestamp", "2026-10-27T18:17:05",
            "reason", "Leg was not fully visible, so this part could not be assessed",
            "confidence", 0.9
        )
    );

    @GetMapping("/")
    public String dashboard(Model model) {

        int totalReps = sessions.stream()
            .mapToInt(s -> (Integer) s.get("rep_count"))
            .sum();

        int totalAttempts = sessions.stream()
            .mapToInt(s -> (Integer) s.get("attempted_reps"))
            .sum();

        model.addAttribute("totalSessions", sessions.size());
        model.addAttribute("totalReps", totalReps);
        model.addAttribute("totalAttempts", totalAttempts);
        model.addAttribute("totalFlags", flags.size());
        model.addAttribute("sessions", sessions);
        model.addAttribute("flags", flags);

        return "dashboard";
    }

    @GetMapping("/sessions/{sessionId}")
    public String sessionDetails(
            @PathVariable String sessionId, Model model) {

        Map<String, Object> session = sessions.stream()
            .filter(s -> sessionId.equals(s.get("session_id")))
            .findFirst()
            .orElse(null);

        if (session == null) {
            return "redirect:/";
        }

        List<Map<String, Object>> sessionFlags = flags.stream()
            .filter(f -> sessionId.equals(f.get("session_id")))
            .toList();

        model.addAttribute("sessionData", session);
        model.addAttribute("flags", sessionFlags);

        return "session-details";
    }
}