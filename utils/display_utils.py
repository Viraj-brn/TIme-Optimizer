def format_schedule_text(schedule):
    lines = ["Your optimized schedule:\n"]
    for s in schedule:
        lines.append(f"{s['start']} - {s['end']}: {s['task']} ({s['energy']})")
    return "\n".join(lines)