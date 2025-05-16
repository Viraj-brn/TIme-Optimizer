import streamlit as st
import json
from scheduler.core import generate_schedule
import matplotlib.pyplot as plt
import os
from datetime import datetime

# -- Save/Load Paths --
SAVE_PATH = "C:/Users\ASUS/OneDrive/Documents/GitHub/Time-Optimizer/data/saved_tasks.json"

def save_tasks(tasks):
    with open(SAVE_PATH, "w") as f:
        json.dump(tasks, f, indent=2)

def load_tasks():
    if os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, "r") as f:
            return json.load(f)
    return []

# -- Page Setup --
st.set_page_config(page_title="Time Optimizer", layout="centered")
st.title("Time Optimizer")
st.markdown("Plan your day smartly based on task priority and energy levels.")

# -- Input: Time Available --
available_hours = st.slider("How many hours are available today?", 1, 14, 6)

# -- Load Saved Tasks --
if st.sidebar.button("Load Last Saved Tasks"):
    tasks = load_tasks()
    st.session_state["loaded_tasks"] = tasks
    st.rerun()

loaded = st.session_state.get("loaded_tasks", [])
task_count = st.number_input("Number of tasks", min_value=1, max_value=10, value=len(loaded) or 3)

# -- Task Input Section --
tasks = []
for i in range(task_count):
    st.markdown(f"**Task {i+1}**")
    name = st.text_input(f"Name {i+1}", value=loaded[i]["name"] if i < len(loaded) else "", key=f"name{i}")
    duration = st.slider(f"Duration (hrs) {i+1}", 1, 4, loaded[i]["duration"] if i < len(loaded) else 1, key=f"dur{i}")
    priority = st.slider(f"Priority (1=Low, 5=High) {i+1}", 1, 5, loaded[i]["priority"] if i < len(loaded) else 3, key=f"pri{i}")
    task_type = st.selectbox(f"Type {i+1}", ["Study", "Work", "Health", "Personal", "Creative"], index=["Study", "Work", "Health", "Personal", "Creative"].index(loaded[i]["type"]) if i < len(loaded) else 0, key=f"type{i}")
    energy = st.selectbox(f"Energy requirement {i+1}", ["high", "medium", "low"], index=["high", "medium", "low"].index(loaded[i]["energy"]) if i < len(loaded) else 0, key=f"en{i}")
    
    if name:
        tasks.append({
            "name": name,
            "duration": duration,
            "priority": priority,
            "type": task_type,
            "energy": energy
        })

# -- Save Button --
if tasks and st.button("Save Task List"):
    save_tasks(tasks)
    st.success("Tasks saved successfully!")

# -- Generate Schedule --
if st.button("Generate Schedule") and tasks:
    schedule = generate_schedule(tasks, available_hours)

    if schedule:
        st.subheader("Optimized Schedule")
        for s in schedule:
            st.markdown(f"**{s['start']} – {s['end']}**: {s['task']} ({s['energy']})")

        # -- Pie Chart --
        st.subheader("Time Distribution")
        labels = [s["task"] for s in schedule]
        sizes = [int(s["end"].split(":")[0]) - int(s["start"].split(":")[0]) for s in schedule]
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)

        # -- Unused Time Info --
        total_used = sum(sizes)
        time_left = available_hours - total_used
        st.info(f"Time left unscheduled: {time_left} hour(s)")
    else:
        st.warning("Not enough time to fit any task!")
