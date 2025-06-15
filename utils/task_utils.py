# Tasks filter by type
def filter_schedule_by_type(schedule, selected_type):
    return [task for task in schedule if task["type"].lower() == selected_type.lower()] if selected_type != "All" else schedule

# Tasks filter by matching tags
def filter_by_tags(schedule, selected_tags):
    return [s for s in schedule if any(tag in selected_tags for tag in s.get("tags", []))]

# Smart suggestions generated based on tag, unused time, and used tasks
def get_smart_suggestions(tasks, used_tasks, unused_time, focus_tag):
    focus_tag_lower = focus_tag.strip().lower()
    return [
        t for t in tasks
        if t["name"] not in used_tasks
        and t["duration"] <= unused_time
        and (focus_tag_lower in [tag.lower() for tag in t.get("tags", [])] if focus_tag_lower else True)
    ]

# utils/task_utils.py

def filter_schedule_by_type_and_tags(schedule, selected_types, selected_tags):
    """
    Filters the schedule based on selected task types and tags.

    Parameters:
    - schedule: List of task dictionaries with 'task_type' and 'tags'.
    - selected_types: List of task types to include.
    - selected_tags: List of tags to include.

    Returns:
    - Filtered schedule list.
    """
    return [
        s for s in schedule
        if s["task_type"] in selected_types and
           (not selected_tags or any(tag in selected_tags for tag in s.get("tags", [])))
    ]
