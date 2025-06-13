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
    time_pointer = 8
    scheduled_tasks = set()

    for energy_level, hours in energy_blocks.items():
        for hour in hours:
            if used_hours >= available_hours:
                break

            best_task = None
            best_score = -1

            for task in tasks:
                if task["name"] in scheduled_tasks:
                    continue
                if used_hours + task["duration"] > available_hours:
                    continue
                if hour + task["duration"] > 22:
                    continue

                score = compute_task_score(task, energy_level, focus_tag)
                if score > best_score:
                    best_score = score
                    best_task = task

            if best_task:
                print(f"[DEBUG] Assigning task: '{best_task['name']}' | Duration: {best_task['duration']}h | Energy: {best_task['energy']} | Slot: {hour}:00 to {hour + best_task['duration']}:00")
                schedule.append({
                    "task": best_task["name"],
                    "start": f"{hour}:00",
                    "end": f"{hour + best_task['duration']}:00",
                    "energy": best_task["energy"]
                })
                used_hours += best_task["duration"]
                scheduled_tasks.add(best_task["name"])

    return schedule

def assign_energy_blocks(available_hours):
    if available_hours<=3:
        return [(0, available_hours, 'high')]
    elif available_hours<=6:
        return [(0, 2, 'high'), (2, available_hours, 'medium')]
    else:
        return [(0, 2, 'high'), (2, 4, 'medium'), (4, available_hours, 'low')]
    
