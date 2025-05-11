def generate_schedule(tasks, available_hours):
    #Sort tasks based on priority
    tasks.sort(key = lambda x:x["priority"], reverse = True)
    energy_blocks = {
        "high":range(8,12), # 8AM to 12OM
        "medium":range(12,16), # 12PM to 4PM
        "low":range(16,22) # 4PM to 10PM
    }
    schedule = []
    used_hours = 0
    time_pointer = 8 #Starts from 8 AM
    for task in tasks:
        if used_hours + task["duration"] > available_hours:
            continue #Skip the task if not enough time left
        
        possible_slots = energy_blocks[task["energy"]]
        for hour in possible_slots:
            if hour >= time_pointer and hour + task["duration"] <= 22:
                schedule.append({"task": task["name"],
                                "start": f"{hour}:00",
                                "end": f"{hour+task['duration']}:00",
                                "energy": task["energy"]
                                }
                )
                used_hours +=task ["duration"]
                time_pointer = hour + task["duration"]
                break
    return schedule