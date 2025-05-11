import json
from scheduler.core import generate_schedule

with open("data/sample_tasks.JSON", "r") as f:
    tasks = json.load(f)

available_hours = 6
schedule = generate_schedule(tasks, available_hours)

for s in schedule:
    print(f"{s['start']} - {s['end']}: {s['task']} ({s['energy']})")