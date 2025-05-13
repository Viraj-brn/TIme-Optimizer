import streamlit as st
import json
from scheduler.core import generate_schedule
import matplotlib.pyplot as plt

st.set_page_config(page_title="Time Optimizer", layout="centered")

st.title("Time OPtimizer")
st.markdown("Plan your day smartly based on task priority and energy levels.")

#Input: Available time
available_hours = st.slider("How many hours are available today?",1, 14, 6)

#Input: Task list
st.subheader("Tasks")
task_count = st.number_input("Number of tasks", min_value=1, max_value=10, value=3)

tasks = []
for i in range(task_count):
    st.markdown(f"**Task{i+1}**")
    name = st.text_input(f"Name{i+1}", key=f"name{i}")
    duration = st.slider(f"Duration(hrs){i+1}", 1, 4, 1, key=f"dur{i}")
    priority = st.slider(f"Priority (1=Low, 5=High) {i+1}", 1, 5, 3, key=f"pri{i}")
    task_type = st.selectbox(f"Type{i+1}", ["Study", "Work", "Health", "Personal", "Creative"], key=f"type{i}")
    energy = st.selectbox(f"Energy requirement {i+1}", ["high", "medium", "low"], key=f"en{i}")
    
    if name:
        tasks.append({
            "name": name, 
            "duration": duration,
            "priority": priority,
            "type": task_type,
            "energy": energy
        })

#Generate Button
if st.button("Generate Schedule") and tasks:
    schedule = generate_schedule(tasks, available_hours)
    
    if schedule:
        st.subheader("Time Distribution")
        
        for s in schedule:
            st.markdown(f"**{s['start']} – {s['end']}**: {s['task']} ({s['energy']})")
            
        #Pie chart for Time Distribution
        st.subheader("Time Distribution")
        labels = [s["task"] for s in schedule]
        sizes = [int(s["end"].split(":")[0]) - int(s["start"].split(":")[0]) for s in schedule]
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)
    else:
        st.warning("Not enough time to fit any task!")