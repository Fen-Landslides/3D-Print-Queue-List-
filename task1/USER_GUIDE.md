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
## Run the Program (Local Mode)

1. Make sure Python 3 is installed on your machine.
2. Open the project folder (the folder that contains `main.py` and `requirements.txt`).
3. Click on the address bar of the folder, type `cmd` and press Enter.
   - A command prompt window will open at this folder.
4. In the command prompt, type:

   pip install -r requirements.txt

   and press Enter to install required packages.
5. After installation finishes, type:

   python main.py

   and press Enter to start the program.
6. The Tkinter window “3D Print Queue System” should appear.

### Method 2: Windows Double-click
Windows users can double-click `run.bat` to launch the program. The batch file runs `main.py` from the correct project folder. [2]

## Documentation
- User Guide: [USER_GUIDE.md](./USER_GUIDE.md)

## Optional Firestore Mode
This project can also use Firestore for multi-device shared access. Firebase Admin SDK supports Firestore access through service account credentials. [3]Click **Return to Waiting**

Result:
- The selected job moves back to **Waiting Queue**
- If PIN is enabled, the system asks for the correct admin PIN

### Step 6: Delete a job
1. Select a job from any list
2. Click **Delete Selected**

Result:
- The selected job is removed from the system
- If PIN is enabled, the system asks for the correct admin PIN

### Step 7: Reorder waiting jobs
1. Select a job in **Waiting Queue**
2. Click **Move Up** or **Move Down**

Result:
- The job priority in the waiting queue changes

***

## 4. PIN Management

### Set or change PIN
1. Click **Set / Remove PIN**
2. A dialog window will appear with:
   - Old PIN
   - New PIN
   - Confirm New PIN
3. If a PIN already exists, enter the old PIN
4. Enter the new PIN and confirm it
5. Click **Save**

Result:
- The PIN is updated
- Sensitive actions will require the PIN

### Remove PIN
1. Click **Set / Remove PIN**
2. Enter the old PIN (if PIN already exists)
3. Leave **New PIN** and **Confirm New PIN** blank
4. Click **Save**

Result:
- PIN protection is removed

***

## 5. Export Functions

### Export all jobs
1. Click **Export All CSV**
2. Choose a save location and file name

Result:
- A CSV file containing all queue records is created

### Export completed jobs by date
1. Click **Export Done by Date**
2. Enter the start date in `YYYY-MM-DD`
3. Enter the end date in `YYYY-MM-DD`
4. Choose a save location

Result:
- A CSV file containing completed jobs within the selected date range is created

***

## 6. Notes
- If no jobs are added, all lists will be empty at startup.
- Local mode is the recommended mode for normal use and assessment.
- Firestore mode is optional and can be used for multi-device shared queue.