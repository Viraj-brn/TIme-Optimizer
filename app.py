import numpy as np
from collections import Counter
import streamlit as st
import json
from scheduler.core import generate_schedule
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import matplotlib.dates as mdates

SAVE_DIR = os.path.join("data")
SAVE_PATH = os.path.join(SAVE_DIR, "saved_tasks.json")
os.makedirs(SAVE_DIR, exist_ok=True)

#Gantt Style Task timeline function
def plot_task_timeline(schedule):
    fig, ax = plt.subplots(figsize = (10,4))
    
    base_time = datetime.strptime("08:00", "%H:%M") #Starting time for display
    for idx, task in enumerate(schedule):
        start = datetime.strptime(task["start"], "%H:%M")
        end = datetime.strptime(task["end"], "%H:%M")
        ax.barh(task["task"], (end - start).seconds/3600, left=(start - base_time).seconds/3600)
    
    ax.set_xlabel("Hours of Day")
    ax.set_ylabel("Tasks")
    ax.set_title("Task timeline")
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    st.pyplot(fig, use_container_width=True)

def save_tasks(tasks):
    with open(SAVE_PATH, "w") as f:
        json.dump(tasks, f, indent=2)

def load_tasks():
    if os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, "r") as f:
            return json.load(f)
    return []

def format_schedule_text(schedule):
    lines = ["Your optimized schedule:\n"]
    for s in schedule:
        lines.append(f"{s['start']} - {s['end']}: {s['task']} ({s['energy']})")
    return "\n".join(lines)

# -- Page Setup --
st.set_page_config(page_title="Time Optimizer", layout="centered")
st.title("Time Optimizer")
st.markdown("Plan your day smartly based on task priority and energy levels.")
st.header("Task Input")

# -- Input: Time Available --
available_hours = st.slider("How many hours are available today?", 1, 14, 6)

# -- Load Saved Tasks --
if st.sidebar.button("Load Last Saved Tasks"):
    tasks = load_tasks()
    if tasks:
        st.session_state["loaded_tasks"] = tasks
        st.rerun()
    else:
        st.sidebar.warning("No saved tasks found")

loaded = st.session_state.get("loaded_tasks", [])
task_count = st.number_input("Number of tasks", min_value=1, max_value=10, value=len(loaded) or 3)

# -- Task Input Section --
st.markdown("Available Time and Task Details")
tasks = []
for i in range(task_count):
    
    loaded_tasks = loaded    
    if i<len(loaded_tasks):
        default = loaded_tasks[i]
    else:
        default = {}

    with st.expander(f"Task{i+1}"):
        name = st.text_input(f"Name {i+1}", value= default.get("name", ""), key=f"name{i}")
        duration = st.slider(f"Duration (hrs) {i+1}", 1, 4, default.get("duration", 1), key=f"dur{i}")
        priority = st.slider(f"Priority (1=Low, 5=High) {i+1}", 1, 5, default.get("priority", 3), key=f"pri{i}")
        task_type = st.selectbox(f"Type {i+1}", ["Study", "Work", "Health", "Personal", "Creative"], index=["Study", "Work", "Health", "Personal", "Creative"].index(default.get("type", "Study")), key=f"type{i}")
        energy = st.selectbox(f"Energy requirement {i+1}", ["high", "medium", "low"], index=["high", "medium", "low"].index(default.get("energy", "medium")), key=f"en{i}")
    
    if name:
        tasks.append({
            "name": name,
            "duration": duration,
            "priority": priority,
            "type": task_type,
            "energy": energy
        })

# -- Save Button --
if st.button("Save Task List"):
    save_tasks(tasks)
    st.success("Tasks saved successfully!")
    
# -- Clear Button --
if st.button("Clear Saved Tasks"):
    if os.path.exists(SAVE_PATH):
        os.remove(SAVE_PATH)
        st.success("Saved Tasks Cleared")
        st.session_state.pop("loaded_tasks", None)
        st.rerun()
        
task_types = sorted(set(task['type'] for task in tasks))
selected_types = st.multiselect("Filter by Task Type", task_types, default=task_types)

# -- Generate Schedule --
if st.button("Generate Schedule") and tasks:
    schedule = generate_schedule(tasks, available_hours)
    task_type_lookup = {t["name"]: t["type"] for t in tasks}
    for s in schedule:
        s["task_type"] = task_type_lookup.get(s["task"], "Unknown")
    filtered_schedule = [s for s in schedule if s["task_type"] in selected_types]
    #Summary stats
    energy_counts = Counter(s['energy'] for s in filtered_schedule)
    type_counts = Counter(s['task_type'] for s in filtered_schedule)
    priorities = [task['priority'] for task in tasks if task['name'] in [s['task'] for s in filtered_schedule]]
    avg_priority = np.mean(priorities) if priorities else 0
    most_common_type = type_counts.most_common(1)[0][0] if type_counts else "N/A"

    if filtered_schedule:
        st.subheader("Filtered Schedule")
        
        type_icons = {
            "Study": "📚",
            "Work": "💼",
            "Health": "💪",
            "Personal": "❤️",
            "Creative": "🎨"
        }
        for s in filtered_schedule:
            icon = type_icons.get(s["task_type"], "🗂️")
            st.markdown(f"***{s['start']} – {s['end']}** &nbsp;  {s['task']} ({s['energy'].capitalize()} energy)")

        st.subheader("Task Summary Dashboard")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("High Energy Tasks", f"{energy_counts.get('high', 0)}")
        
        with col2:
            st.metric("Medium Energy", f"{energy_counts.get('medium', 0)}")
        
        with col3:
            st.metric("Low Energy", f"{energy_counts.get('low', 0)}")
        st.markdown(f"**Most Frequent Task type**: {most_common_type}")
        st.markdown(f"**Average Priority**: {avg_priority:.2f}")
    
       # -- Pie Chart --
        st.subheader("Time Distribution")
        labels = [s["task"] for s in filtered_schedule]
        sizes = [int(s["end"].split(":")[0]) - int(s["start"].split(":")[0]) for s in filtered_schedule]
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)
        schedule_text = format_schedule_text(filtered_schedule)
        st.download_button("Download schedule as .txt", schedule_text, file_name="schedule.txt")

        #Bar Chart
        st.subheader("Hour spent per task type")
        type_hours = {}
        for s in filtered_schedule:
            hrs = int(s["end"].split(":")[0]) - int(s["start"].split(":")[0])
            type_hours[s["task_type"]] = type_hours.get(s["task_type"], 0) + hrs
            
        fig2, ax2 = plt.subplots()
        ax2.bar(type_hours.keys(), type_hours.values(), color = 'skyblue')
        ax2.set_ylabel("Hours")
        ax2.set_xlabel("Task Type")
        st.pyplot(fig2, use_container_width=True)
        
        st.subheader("Task Timeline (Gantt View)")
        plot_task_timeline(schedule)
        
        # -- Unused Time Info --
        total_used = sum(sizes)
        time_left = available_hours - total_used
        if time_left>=2:
            st.warning(f"Warning: {time_left} hour(s) left unscheduled.")
        else:
            st.warning(f"Good Job! Only {time_left} hour(s) left unschedule.")
    else:
        st.warning("Not enough time to fit any task!")
