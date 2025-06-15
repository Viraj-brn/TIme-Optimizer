import os
import json
from datetime import datetime

#Defining directories and file paths
SAVE_DIR = os.path.join("data")
SAVE_PATH = os.path.join(SAVE_DIR, "saved_tasks.json")
TODAY_SCHEDULE_PATH = os.path.join(SAVE_DIR, f"schedule_{datetime.now().strftime('%Y%m%d')}.json")

os.makedirs(SAVE_DIR, exist_ok=True) #create directory if not there

#Saving task to disk
def save_tasks(tasks):
    with open(SAVE_PATH, "w") as f:
        json.dump(tasks, f, indent=2)
        

#Load task
def load_tasks():
    if os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, "r") as f:
            data = json.load(f)
            return data.get("tasks", []), data.get("last_updated", "Unknown")
    return [], "Unknown"

#Saving and loading today's schedule separeately
def save_today_schedule(schedule):
    with open(TODAY_SCHEDULE_PATH, "w") as f:
        json.dump(schedule, f, indent=2)

def load_today_schedule():
    if os.path.exists(TODAY_SCHEDULE_PATH):
        with open(TODAY_SCHEDULE_PATH, "r") as f:
            return json.load(f)
    return []