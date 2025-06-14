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
TODAY_SCHEDULE_PATH = os.path.join(SAVE_DIR, f"schedule_{datetime.now().strftime('%Y%m%d')}.json")

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
    data = {
        "tasks": tasks,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(SAVE_PATH, "w") as f:
        json.dump(tasks, f, indent=2)

def load_tasks():
    if os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, "r") as f:
            data = json.load(f)
            return data.get("tasks", []), data.get("last_updated", "Unknown")
    return []

def save_today_schedule(schedule):
    with open(TODAY_SCHEDULE_PATH, "w") as f:
        json.dump(schedule, f, indent=2)

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
    tasks, last_updated = load_tasks()
    st.sidebar.success(f"Tasks Loaded (Last updated: {last_updated})")
    if tasks:
        st.session_state["loaded_tasks"] = tasks
        st.rerun()
    else:
        st.sidebar.warning("No saved tasks found")

# View today's schedule
if st.sidebar.button("View Today’s Schedule"):
    filter_options = ["All", "Study", "Work", "Health", "Personal", "Creative"]
    selected_type = st.sidebar.selectbox("Filter by Task Type", filter_options)
    
    if os.path.exists(TODAY_SCHEDULE_PATH):
        with open(TODAY_SCHEDULE_PATH, "r") as f:
            today_schedule = json.load(f)
        
        if selected_type != "All":
            filtered_schedule = [task for task in today_schedule if task["type"].lower() == selected_type.lower()]
        else:
            filtered_schedule = today_schedule

        st.sidebar.subheader("Today’s Schedule")
        st.sidebar.text(format_schedule_text(filtered_schedule))
        plot_task_timeline(filtered_schedule)  # Optional visualization
    else:
        st.sidebar.warning("No schedule saved for today.")

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

    col1, col2 = st.columns([5, 1])
    with col1.expander(f"Task{i+1}"):
        name = st.text_input(f"Name {i+1}", value= default.get("name", ""), key=f"name{i}")
        duration = st.slider(f"Duration (hrs) {i+1}", 1, 4, default.get("duration", 1), key=f"dur{i}")
        priority = st.slider(f"Priority (1=Low, 5=High) {i+1}", 1, 5, default.get("priority", 3), key=f"pri{i}")
        task_type = st.selectbox(f"Type {i+1}", ["Study", "Work", "Health", "Personal", "Creative"], index=["Study", "Work", "Health", "Personal", "Creative"].index(default.get("type", "Study")), key=f"type{i}")
        energy = st.selectbox(f"Energy Requirement {i+1}", ["high", "medium", "low"], index=["high", "medium", "low"].index(default.get("energy", "medium")), key=f"en{i}")
        tags_input = st.text_input(f"Tags (comma separated) {i+1}", value=",".join(default.get("tags", [])), key=f"tags{i}")
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
    
    with col2:
        if st.button("X", key=f"del{i}"):
            st.session_state["deleted_task_ids"] = st.session_state.get("deleted_task_ids", set())
            st.session_state["deleted_task_ids"].add(i)
            st.rerun()
        
    if name and i not in st.session_state.get("deleted_task_ids", set()):
        tasks.append({
            "name": name,
            "duration": duration,
            "priority": priority,
            "type": task_type,
            "energy": energy,
            "tags" : tags
        })

# -- Undo All Deletes Button --
if "deleted_task_ids" in st.session_state and st.session_state["deleted_task_ids"]:
    if st.button("Undo All Deletes"):
        st.session_state.pop("deleted_task_ids", None)
        st.rerun()

# -- Save Button --
if st.button("Save Task List"):
    save_tasks(tasks)
    st.success("Tasks saved successfully!")
    
if st.button("Update Saved Tasks"):
    save_tasks(tasks)
    st.success("Saved tasks updated")
    
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
focus_tag = st.text_input("Today's Focus Tag(optional)", "")    
if st.button("Generate Schedule") and tasks:
    schedule = generate_schedule(tasks, available_hours, focus_tag)
    save_today_schedule(schedule)
    st.success("Today's schedule saved!")
    all_tags = sorted({tag for s in schedule for tag in s.get("tags", [])})
    selected_tags = st.sidebar.multiselect("Filter by tags", all_tags, default = all_tags)
    task_type_lookup = {t["name"]: t["type"] for t in tasks}
    task_tags_lookup = {t["name"]: t.get("tags", []) for t in tasks}
    for s in schedule:
        s["task_type"] = task_type_lookup.get(s["task"], "Unknown")
        s["tags"] = task_tags_lookup.get(s["task"], [])
    
    filtered_schedule = [
    s for s in schedule
    if s["task_type"] in selected_types and
       (not selected_tags or any(tag in selected_tags for tag in s.get("tags", [])))
    ]
    
    #Summary stats
    energy_counts = Counter(s['energy'] for s in filtered_schedule)
    type_counts = Counter(s['task_type'] for s in filtered_schedule)
    priorities = [task['priority'] for task in tasks if task['name'] in [s['task'] for s in filtered_schedule]]
    avg_priority = np.mean(priorities) if priorities else 0
    most_common_type = type_counts.most_common(1)[0][0] if type_counts else "N/A"

    if filtered_schedule:
        st.subheader("Manual Adjustments (Drag to reorder)")
        
        for idx, task in enumerate(filtered_schedule):
            task["order"] = idx
            
        edited_schedule = st.data_editor(filtered_schedule, 
                                         column_order=["order", "start", "end", "task", "energy", "task_type", "tags"],
                                         use_container_width=True, num_rows="fixed")

        if st.button("Apply Manual Edits and Save"):
            edited_schedule.sort(key = lambda x: x["order"])
            save_today_schedule(edited_schedule)
            st.success("Custom schedule applied!")
            
            filtered_schedule = edited_schedule
        
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
            tag_str = ", ".join(s.get("tags", []))
            st.markdown(f"***{s['start']} – {s['end']}** &nbsp;  {s['task']} ({s['energy'].capitalize()} energy){' | ' + tag_str if tag_str else ''}")

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
        
        # -- Daily Insights Summary --
        st.subheader("Daily Insights")
        total_tasks = len(filtered_schedule)
        total_duration = sum(int(s["end"].split(":")[0]) - int(s["start"].split(":")[0]) for s in filtered_schedule)
        energy_count = Counter(s["energy"] for s in filtered_schedule)
        type_duration = {}
        priority_map = {s['task']: next((t['priority'] for t in tasks if t["name"] == s["task"]), 0) for s in filtered_schedule}
        max_priority_task = max(priority_map.items(), key = lambda x: x[1])[0] if type_duration else "None"
        
        for s in filtered_schedule:
            hrs = int(s["end"].split(":")[0]) - int(s["start"].split(":")[0])
            type_duration[s["task_type"]] = type_duration.get(s["task_type"], 0) + hrs
        
        max_type = max(type_duration.items(), key=lambda x: x[1])[0] if type_duration else "N/A"
        completion_percent = round((total_duration/ available_hours) * 100, 1) if available_hours else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tasks", total_tasks)
        col2.metric("Total Hours Used", total_duration)
        col3.metric("percent(%) of day utilized", f"{completion_percent}%")
        
        col4, col5, col6 = st.columns(3)
        col4.metric("Most Time Type", max_type)
        col5.metric("High Energy Tasks", energy_count.get("high", 0))
        col6.metric("Top Priority Task", max_priority_task)
        
        if completion_percent >=90:
            st.success("You are killing it! Almost a fully packed day.")
        elif completion_percent >=60:
            st.info("Solid work! You can try to squeeze in one more task.")
        else:
            st.warning("You still have time! Fill it with something meaningful")
        
        # -- Smart Suggestions Block --
        st.subheader("Smart Suggestions")
        
        unused_time = available_hours - total_duration
        
        if unused_time <= 0:
            st.info("You're fully scheduled. No more suggestions for today.")
        else:
            st.markdown(f"You have **{unused_time} hour(s)** still available")
            st.markdown("Here are some suggestions from your saved tasks:")
            
            focus_tag_lower = focus_tag.strip().lower()
            remaining_tasks = [
                t for t in tasks
                if t["name"] not in [s["task"] for s in filtered_schedule]
                and t["duration"] <= unused_time
                and (focus_tag_lower in [tag.lower() for tag in t.get("tags", [])] if focus_tag_lower else True)
            ]
            
            sorted_suggestions = sorted(remaining_tasks, key=lambda x: (x["priority"], x["energy"] == "low"), reverse=True)
            
            if sorted_suggestions:
                for suggestion in sorted_suggestions[:5]:
                    tags_string = ", ".join(suggestion.get("tags", []))
                    st.markdown(f"• **{suggestion['name']}** ({suggestion['duration']} hr, {suggestion['energy']} energy) — _Tags: {tags_string}_")
            else:
                st.info("No suitable tasks found matching the focus tag or time")
        st.subheader("Task Timeline (Gantt View)")
        plot_task_timeline(filtered_schedule)
        
        # -- Unused Time Info --
        total_used = sum(sizes)
        time_left = available_hours - total_used
        if time_left>=2:
            st.warning(f"Warning: {time_left} hour(s) left unscheduled.")
        else:
            st.warning(f"Good Job! Only {time_left} hour(s) left unschedule.")
    else:
        st.warning("Not enough time to fit any task!")
