def compute_task_score(task, block_energy, focus_tag):
    score = 0

    # Priority weight
    score += task["priority"] * 10

    # Energy match weight
    energy_weights = {
        ("high", "high"): 15,
        ("medium", "medium"): 10,
        ("low", "low"): 10,
        ("high", "medium"): 5,
        ("medium", "low"): 2,
    }
    score += energy_weights.get((task["energy"], block_energy), 0)

    # Focus tag weight
    if focus_tag:
        tag_list = [tag.lower() for tag in task.get("tags", [])]
        if focus_tag.lower() in tag_list:
            score += 10

    return score


def generate_schedule(tasks, available_hours, focus_tag=""):
    energy_blocks = {
        "high": range(8, 12),     # 8AM - 12PM
        "medium": range(12, 16),  # 12PM - 4PM
        "low": range(16, 22)      # 4PM - 10PM
    }

    schedule = []
    used_hours = 0
    scheduled_tasks = set()
    occupied_hours = set()  # ❗ Tracks all hours already scheduled

    for energy_level, hours in energy_blocks.items():
        for hour in hours:
            if used_hours >= available_hours:
                break

            # Skip if current hour is already occupied
            if hour in occupied_hours:
                continue

            best_task = None
            best_score = -1

            for task in tasks:
                duration = task["duration"]
                task_hours = range(hour, hour + duration)

                # Skip if:
                # - Already scheduled
                # - Not enough time left
                # - Will exceed working window (i.e., 22)
                # - Any of the task's hours are occupied
                if (
                    task["name"] in scheduled_tasks or
                    used_hours + duration > available_hours or
                    hour + duration > 22 or
                    any(h in occupied_hours for h in task_hours)
                ):
                    continue

                score = compute_task_score(task, energy_level, focus_tag)
                if score > best_score:
                    best_score = score
                    best_task = task

            if best_task:
                duration = best_task["duration"]
                start = hour
                end = hour + duration

                print(f"[DEBUG] Assigning task: '{best_task['name']}' | Duration: {duration}h | Energy: {best_task['energy']} | Slot: {start}:00 to {end}:00")

                schedule.append({
                    "task": best_task["name"],
                    "start": f"{start}:00",
                    "end": f"{end}:00",
                    "energy": best_task["energy"],
                    "tags": ", ".join(best_task.get("tags", []))
                })

                used_hours += duration
                scheduled_tasks.add(best_task["name"])
                occupied_hours.update(range(start, end))  # ❗ Mark these hours as used

    return schedule

def assign_energy_blocks(available_hours):
    if available_hours<=3:
        return [(0, available_hours, 'high')]
    elif available_hours<=6:
        return [(0, 2, 'high'), (2, available_hours, 'medium')]
    else:
        return [(0, 2, 'high'), (2, 4, 'medium'), (4, available_hours, 'low')]
    
