# 🧠 Time Optimizer – Smart Productivity Scheduler

A personalized scheduling app that creates optimal daily plans based on task priority, energy levels, and productivity patterns. Built with Python and Streamlit.

---

## 🚀 Features

- ✍️ Add tasks with priority, duration, energy requirements, and type
- 📅 Generate optimized daily schedules using greedy logic
- 📊 Visualize time allocation across tasks and categories
- 🤖 Predict productivity score (with basic ML modeling)
- 📂 Save and load personal task profiles
- 🌐 Deployed via Streamlit Cloud (coming soon)

---

## 📥 Inputs

- Daily available hours
- List of tasks:
  - Name
  - Estimated duration (hrs)
  - Priority (1–5)
  - Task type (e.g., Study, Health, Work)
  - Energy requirement (Low / Medium / High)

---

## 📤 Outputs

- Optimized daily time block schedule
- Visual charts for:
  - Task category distribution
  - Energy-based task placement
- Productivity score (predicted)

---

## 🛠️ Tech Stack

- Python
- Streamlit
- Pandas, NumPy
- Matplotlib / Plotly
- Scikit-learn

---

## 📁 Project Structure

time-optimizer/
├── app.py
├── scheduler/
│ └── core.py
├── ml/
│ └── model.py
├── data/
│ └── sample_tasks.json
├── utils/
│ └── helpers.py
├── assets/
├── requirements.txt
└── README.md


---

## 🔮 Future Improvements

- User login and task history
- Calendar integration
- Advanced ML to recommend task timings

---

## 🤝 Contributing

Pull requests welcome! For major changes, please open an issue first to discuss what you’d like to change.

---

## 📜 License


