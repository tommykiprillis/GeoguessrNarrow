# GeoGuessr Narrower

A web-based tool for narrowing down possible GeoGuessr countries based on visible features.

🌐 **Live Demo:** [https://geoguessrnarrow.onrender.com](https://geoguessrnarrow.onrender.com)

---

## Overview

**GeoGuessr Narrower** helps players identify potential countries by selecting observable features from Street View imagery. The application provides real-time matching against a database of country characteristics.

Simply select features you see in the image (climate, architecture, signs, etc.) and instantly get a ranked list of matching countries with match percentages.

---

## Features

- **Interactive Feature Selection** — Click-based interface to select observed features
- **Real-time Matching** — Instant country matching with percentage scores
- **Feature Management** — Extensible system for adding new countries and features
- **Dark/Light Mode** — Theme toggle with persistent preference
- **Visual Feedback** — Color-coded results based on match scores
- **Responsive Design** — Works on desktop and mobile

---

## Project Structure

```
GeoGuessr-NarrowDown/
├── src/                          # Frontend & backend source
│   ├── app.py                   # FastAPI backend server
│   ├── index.html               # Web interface
│   ├── script.js                # Frontend logic
│   └── styles.css               # Styling with light/dark themes
├── data/                         # Database files
│   ├── countries.json           # Country-specific feature assignments
│   ├── features.json            # Feature definitions (categories, features, values)
│   └── template.json            # Empty template for new countries
├── scripts/                      # Management & utility scripts
│   ├── add_country.py           # Interactive script to add new countries
│   ├── add_feature.py           # Interactive script to add new features
│   ├── update_country.py        # Update existing country entries
│   ├── delete_country.py        # Remove countries from database
│   ├── rename_category.py       # Rename feature categories
│   ├── script_features_to_template.py  # Auto-assign features to countries
│   └── narrower.py              # Command-line testing tool
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── Procfile                     # Render deployment configuration
└── README.md                    # This file
```

---

## Local Development

### Prerequisites

- Python 3.8+
- pip

### Setup

1. **Clone the repository:**

    ```bash
    git clone <your-repo-url>
    cd GeoGuessr-NarrowDown
    ```

2. **Create a virtual environment:**

    ```bash
    python -m venv venv

    # On Windows
    .\venv\Scripts\Activate.ps1

    # On macOS/Linux
    source venv/bin/activate
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the backend:**

    ```bash
    cd src
    python -m uvicorn app:app --reload
    ```

5. **Open in browser:**
    - Navigate to `http://localhost:8000`
    - Start selecting features to test

---

## Managing Data

### Add a New Country

```bash
python scripts/add_country.py
```

Follow the interactive prompts to add a new country and assign features.

### Add a New Feature Category

```bash
python scripts/add_feature.py
```

Create new feature categories and values.

### Update Feature Assignments

```bash
python scripts/script_features_to_template.py
```

Automatically assigns new features to existing countries based on the template.

### Other Management Scripts

- `update_country.py` — Edit existing country data
- `delete_country.py` — Remove a country
- `rename_category.py` — Rename a feature category
- `narrower.py` — Test the matching algorithm from command line

---

## Deployment

This project is deployed on **Render** and automatically redeploys on every push to the main branch.

### Deploy Your Own Fork

1. **Make the repository public** on GitHub
2. **Go to [render.com](https://render.com)**
3. **Create a new Web Service:**
    - Connect your GitHub repository
    - Build Command: `pip install -r requirements.txt`
    - Start Command: `uvicorn src.app:app --host 0.0.0.0 --port $PORT`
4. **Get your Render URL** and update `src/script.js` if needed
5. **Deploy!** — Render auto-deploys on every GitHub push

---

## Technology Stack

- **Backend:** FastAPI (Python)
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Data Format:** JSON
- **Server:** Uvicorn ASGI
- **Deployment:** Render

---

## License

This project is provided as-is for personal use.
