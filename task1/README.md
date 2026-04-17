# 3D Print Queue System

A Python OOP Tkinter application for managing a shared 3D printer queue. It supports adding print jobs, managing waiting / in-progress / completed jobs, protecting sensitive operations with an admin PIN, and exporting queue records to CSV. The project is implemented as a modular Python application with multiple modules/files, which fits the Task 1 OOP-based application requirement. [1]

## Main Features
- Add print jobs with description, ETA, and material/color
- View waiting, in-progress, and completed jobs
- Start the next job and complete selected jobs
- Return jobs to waiting or delete jobs
- Reorder waiting queue with move up / move down
- Set, change, or remove admin PIN through one dialog window
- Export all jobs or completed jobs to CSV

## OOP Concepts Used
- **Encapsulation**: `PrintJob` controls status changes through methods such as `start()` and `complete()`
- **Inheritance**: `LocalRepository` and `FirestoreRepository` inherit from `BaseRepository`
- **Polymorphism**: `QueueManager` works with different repository implementations through the same interface
- **Abstraction**: storage and notification details are separated from business logic

## Project Structure
- `run.bat` – Windows double-click launcher
- `main.py` – application entry point
- `models/` – data models and enums
- `services/` – queue, PIN, export, notification logic
- `repositories/` – local / Firestore storage
- `interfaces/` – Tkinter GUI
- `utils/` – helper files

## Run the Program
### Method 1: Command Line
```bash
pip install -r requirements.txt
python main.py
```

### Method 2: Windows Double-click
Windows users can double-click `run.bat` to launch the program. The batch file runs `main.py` from the correct project folder. [2]

## Documentation
- User Guide: [USER_GUIDE.md](./USER_GUIDE.md)

## Optional Firestore Mode
This project can also use Firestore for multi-device shared access. Firebase Admin SDK supports Firestore access through service account credentials. [3]

```