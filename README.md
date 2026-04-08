# 📚 BookVisualizer

A full-stack application for visualizing books with the help of AI — built with FastAPI (backend) and ReactJS (frontend).

---

## 🚀 Getting Started

These instructions will help you set up your development environment.

---

## 🗃️ Project Structure

```
BookVisualizer/                                     │ Project Name
    ├── backend/                                    │ FastAPI Backend Code
    │   ├── .venv/                                  │ Library Root
    │   ├── App/                                    │
    │   │   ├── ai/                                 │ Python Package
    │   │   │   ├── __init__.py                     │
    │   │   │   ├── api_module.py                   │ Handles Summarization, audio         
    │   │   │   ├── prompt.py                       │
    │   │   │   ├── secret-key.json                 │ json file for audio module from GCC                        
    │   │   │   └── utils.py                        │ 
    │   │   ├── api/                                │ Python Package
    │   │   │   ├── __init__.py                     │
    │   │   │   ├── controllers/                    │ Handles endpoints (Python Package)
    │   │   │   │   ├── __init__.py                 │
    │   │   │   │   └── sigin_controller.py         │
    │   │   │   └── services/                       │ Handles endpoints logic (Python Package)
    │   │   │       ├── __init__.py                 │
    │   │   │       └── sigin_service.py            │
    │   │   ├── dao/                                │ Data Access Object -> MongoDB interaction (Python Package)
    │   │   │   ├── __init__.py                     │
    │   │   │   └── user_dao.py                     │
    │   │   ├── dto/                                │ Pydantic Models (Python Package)
    │   │   │   ├── __init__.py                     │
    │   │   │   └── request_dto.py                  │
    │   │   ├── exceptions/                         │ Handles Exceptions (Python Package)
    │   │   │   ├── __init__.py                     │
    │   │   │   └── exception_handler.py            │
    │   │   ├── utils/                              │ Utilities (Python Package)
    │   │   │   ├── __init__.py                     │
    │   │   │   └── hashing.py                      │
    │   │   ├── vo/                                 │ Database Schema (Python Package)
    │   │   │   ├── __init__.py                     │
    │   │   │   └── book_vo.py                      │
    │   │   ├── __init__.py                         │
    │   │   ├── config.py                           │ Configuration file for DB
    │   │   └── main.py                             │ FastAPI entry point (API Setup)
    │   ├── .env                                    │ Handles the Sensetive Data Required for Project
    │   └── requirements.txt                        │ Backend Dependencies
    │                                               │
    ├── frontend/                                   │ ReactJs Frontend Code
    │   ├── ReactApp/                               │
    │   │   ├── node_modules/                       │ Library Root
    │   │   ├── public/                             │ Public File
    │   │   ├── src/                                │ ReactJs Source Code
    │   │   │   ├── components/                     │ Reusable UI Components
    │   │   │   │   ├── Header/                     │
    │   │   │   │   │   └── Header.js               │
    │   │   │   │   └── Dashboard/                  │
    │   │   │   │       └── DashboardPage.js        │
    │   │   │   ├── api.js                          │ Handles Axios
    │   │   │   ├── App.js                          │ Main ReactJs component
    │   │   │   └── index.js                        │ ReactJs entry point
    │   │   ├── package.json                        │ Frontend dependencies and scripts
    │   │   └── package-lock.json                   │
    │   └── Dockerfile                              │ Docker Configuration for frontend
    │                                               │
    ├── logs/                                       │ Handles Logs
    │   ├── book_visualizer.2025-03-31.zip          │ stores the older log
    │   └── book_visualizer.log                     │ gets the latest logs
    │                                               │
    ├── uploaded_books/                             │ Stores the book an its content based on the AI Output in a mannered structure
    │                                               │
    ├── .gitignore                                  │ Git ignore file to exclude unnecessary files
    └── README.md                                   │ Project Documentation 
```

## ⚙️ Backend Setup (FastAPI)

---
### 1. Create a Virtual Environment

```bash
  cd backend
  python3 -m venv .venv
  source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
````
### 2. Install Dependencies

```bash
  pip install -r requirements.txt
```
### 3. Environment Variables
``` 
Create a .env file inside backend/App/ and add the following:
# Application
DOMAIN = "http://127.0.0.1:8000"
FRONTEND_DOMAIN = "http://127.0.0.1:3000"
DEFAULT_SECRET_KEY = "your-secret-key"
ORIGINS = ['*', 'http://localhost:3000']
SUPPORT_MAIL = "support@example.com"

# Middlewares
SESSION_MIDDLEWARE_SECRET = "your-session-secret"

# Database
MONGODB_URI = "mongodb://localhost:port"

# Tokenization
JWT_TOKEN_SECRET = "your-jwt-secret"

# Mailing
GOOGLE_MAIL_ID = "your-email@example.com"
GOOGLE_MAIL_PASSWORD = "your-email-app-password"

# AI Integrations
HF_API = "your-huggingface-api"
GROQ_API = "your-groq-api"
IMAGE_KEY = "your-runware-api"
```
### 4. Run the Backend
```bash 
  cd App
  uvicorn main:app --reload
```
The frontend will run on http://localhost:3000


## 🎨 Frontend Setup (ReactJS)

---
### 1. Install Dependencies

```bash
  cd frontend/ReactApp
  npm install
````
### 2. Run the Frontend

```bash
  npm start  
````
The frontend will run on http://localhost:3000

## Important

---
Need to download the secret-key.JSON (service account) from the Google Cloud Console and add it
```bash
  cd backend/ai
```

## 📩 Contact

---
For issues, please contact: support@BookVisualiser.com

## 👥 Contributors

---
- Meet Bhanushali (https://github.com/TheMeetB)
- Lay Thakkar
- Nikunj Pandey
- Jay Nai
