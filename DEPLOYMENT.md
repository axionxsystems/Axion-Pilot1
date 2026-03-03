# Deployment Guide

## 1. Backend (FastAPI)

### Deploy on Render.com / Railway / Fly.io

1.  **Repository Setup**: Push your code to GitHub.
2.  **Environment Variables**:
    *   `GROQ_API_KEY`: Your Groq API Key.
    *   `OPENROUTER_API_KEY`: (Optional) If using OpenRouter.
3.  **Build Command**: `pip install -r backend/requirements.txt`
4.  **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port 10000` (Release path might vary depending on where requirements are).
    *   *Note*: Ensure you set the Root Directory to `.` or `backend` depending on your repo structure. Recommended is root, and adjust commands.

## 2. Frontend (Next.js)

### Deploy on Vercel (Recommended)

1.  **Import Project**: Select your GitHub repo in Vercel.
2.  **Root Directory**: Set to `frontend`.
3.  **Framework Preset**: Select Next.js.
4.  **Environment Variables**:
    *   `NEXT_PUBLIC_API_URL`: The URL of your deployed Backend (e.g., `https://my-backend.onrender.com/api`).
5.  **Deploy**: Click Deploy.

## Local Development

**Backend**:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```
