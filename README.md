# Project Pilot - AI Project Generator SaaS

Project Pilot is an AI-powered SaaS platform designed to help students generate complete academic projects, including reports, presentations, and code, in minutes. It features a premium, Apple-inspired UI and a robust FastAPI backend.

## 🚀 Features

- **AI Project Generation**: Generate abstract, architecture, and full source code.
- **Viva Assistant**: AI-powered mock interviewer to prepare for project defense.
- **Premium UI/UX**: Built with Next.js, Tailwind CSS, and Shadcn UI, featuring a high-end "Linear-like" design.
- **Document Generation**: Auto-generate industry-standard PDF reports and PPT presentations.
- **Role-Based Auth**: Secure authentication for Admins and Users.
- **Dashboard**: Comprehensive dashboard for managing projects and generated assets.

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS, Shadcn UI, Framer Motion
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **AI**: Gemini / OpenAI Integration
- **Doc Gen**: Python-docx, Python-pptx

## 📦 Project Structure

```bash
├── frontend/          # Next.js frontend application
│   ├── app/           # App router pages
│   ├── components/    # Reusable UI components
│   └── services/      # API client services
└── backend/           # FastAPI backend application
    ├── app/           # Application logic
    ├── models/        # Database models
    └── main.py        # Entry point
```

## ⚡ Local Setup

### Prerequisites
- Node.js 18+
- Python 3.9+

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```
 Backend will run at `http://localhost:8000`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will run at `http://localhost:3000`

## 🔑 Environment Variables

See `.env.example` for the required environment variables.
Copy `.env.example` to `.env` in both `frontend` and `backend` directories and populate the values.

## 🗺️ Roadmap

- [x] Basic Project Generation
- [x] Premium Dashboard UI
- [x] Viva Assistant
- [ ] Stripe Integration (Payments)
- [ ] Team Collaboration
- [ ] GitHub Integration for direct pushing

## 📄 License

Proprietary - All rights reserved.
