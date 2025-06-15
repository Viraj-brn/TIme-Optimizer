import matplotlib.pyplot as plt
from datetime import datetime
import streamlit as st
import matplotlib.dates as mdates

#Plotting timeline chart
def plot_task_timeline(schedule):
    fig, ax = plt.subplots(figsize=(10, 4))
    base_time = datetime.strptime("08:00", "%H:%M")

    for task in schedule:
        start = datetime.strptime(task["start"], "%H:%M")
        end = datetime.strptime(task["end"], "%H:%M")
        ax.barh(task["task"], (end - start).seconds / 3600, left=(start - base_time).seconds / 3600)

    ax.set_xlabel("Hours of Day")
    ax.set_ylabel("Tasks")
    ax.set_title("Task timeline")
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    st.pyplot(fig, use_container_width=True)