# BorderWatch — Border Monitoring & Incident Reporting System

A full-stack academic project built with Python (Flask), SQLite, and OpenCV.

---

## Project Structure

```
borderwatch/
├── app.py                     # Flask application entry point
├── setup.py                   # DB initialization script
├── requirements.txt
├── borderwatch.db             # SQLite database (auto-created)
├── uploads/                   # Uploaded evidence images
├── models/
│   ├── __init__.py
│   ├── database.py            # DB connection, schema, seed data
│   └── image_processor.py     # OpenCV image analysis
├── routes/
│   ├── __init__.py
│   ├── auth.py                # Login, logout, image serving
│   ├── officer.py             # Officer dashboard & reporting
│   └── admin.py               # Admin dashboard & status updates
├── templates/
│   ├── base.html              # Base layout with navbar
│   ├── login.html             # Login page
│   ├── officer_dashboard.html # Officer's incident list
│   ├── report_incident.html   # Incident submission form
│   ├── admin_dashboard.html   # Admin overview + filters
│   └── incident_detail.html   # Detailed view (shared)
└── static/
    ├── css/
    │   └── style.css          # Tactical dark-theme UI
    └── js/
        └── main.js            # Client-side interactions
```

---

## Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher
- pip

### 2. Install Dependencies

```bash
cd borderwatch
pip install -r requirements.txt
```

> **Note:** If `opencv-python` fails on a headless server, use:
> ```bash
> pip install opencv-python-headless numpy flask werkzeug
> ```

### 3. Initialize the Database

```bash
python setup.py
```

This creates `borderwatch.db` and seeds three default users.

### 4. Run the Application

```bash
python app.py
```

Visit **http://127.0.0.1:5000** in your browser.

---

## Default Login Credentials

| Role    | Username  | Password    |
|---------|-----------|-------------|
| Admin   | admin     | admin123    |
| Officer | officer1  | officer123  |
| Officer | officer2  | officer456  |

---

## Features Overview

### Border Officer
- Login to personal dashboard
- View all their submitted incidents with status
- Submit new incidents with: type, location, description, severity
- Optionally upload an evidence image (auto-analyzed by OpenCV)
- View incident details including image and CV analysis

### Admin
- View ALL incidents from all officers
- Filter by severity (Low/Medium/High), status, and date
- View full incident details and uploaded images
- Update incident status: Reported → Under Investigation → Resolved

### Image Processing (OpenCV)
When an image is uploaded:
1. Grayscale conversion
2. Canny edge detection — measures edge density
3. Gaussian blur + threshold + contour detection — counts distinct regions
4. Brightness analysis
5. Result flagged as **SUSPICIOUS** or **CLEAR** with metrics

---

## Database Schema

```sql
users       (id, username, password, role, full_name, created_at)
incidents   (id, type, location, description, severity, status, datetime, user_id)
images      (id, file_path, analysis_result, incident_id, uploaded_at)
```

---

## Tech Stack

| Layer      | Technology              |
|------------|-------------------------|
| Backend    | Python 3, Flask         |
| Database   | SQLite (via sqlite3)    |
| Images     | OpenCV, NumPy           |
| Frontend   | HTML5, CSS3, Vanilla JS |
| Fonts      | Google Fonts (Rajdhani, Share Tech Mono, Exo 2) |

---

## Academic Notes
This is a demonstration project. No advanced security (hashing, CSRF, sessions expiry) has been implemented to keep the codebase simple and readable.
