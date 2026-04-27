# 🚀 AxionX - Complete Startup Guide

## Quick Start (Windows)

### Option 1: Start Everything Together (EASIEST)
1. Double-click: `start-all.bat` in the project root
2. Wait for both servers to start
3. Open http://localhost:3000

**That's it!** Both backend and frontend will start automatically.

---

### Option 2: Start Servers Separately

#### Terminal 1: Start Backend
```bash
cd backend
python start-backend.bat
```

Wait for:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### Terminal 2: Start Frontend
```bash
cd frontend
npm run dev
```

Wait for:
```
> Local:        http://localhost:3000
```

Then open http://localhost:3000 in your browser.

---

## Quick Start (Mac/Linux)

### Start Everything Together
```bash
chmod +x start-all.sh
./start-all.sh
```

### Start Servers Separately

**Terminal 1 - Backend:**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## Troubleshooting

### "Backend not running" Error
1. Ensure Python is installed: `python --version`
2. Check backend dependencies: `python backend/check_backend.py`
3. Try manual start: `cd backend && python -m uvicorn app.main:app --reload --port 8000`

### "Port already in use" Error
Backend port 8000 is in use:
```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Mac/Linux

# Kill the process
taskkill /PID <PID> /F
```

### "API Not Found" Error on Login
1. Verify backend is running on http://localhost:8000/health
2. Check frontend .env.local has: `NEXT_PUBLIC_API_URL=http://localhost:8000/api`
3. Verify API is accessible: http://localhost:8000/docs

### Browser Shows "Connecting to localhost:3000"
Frontend is still building. Wait 30-60 seconds and refresh.

---

## Testing Login

**Test Credentials**
```
Email: admin@example.com
Password: (Check backend/.env for sample user)
```

Or create a new account via the signup page.

---

## API Documentation

Once running, visit:
- **Backend Docs:** http://localhost:8000/docs
- **Backend Health:** http://localhost:8000/health

---

## Advanced Commands

### Check Backend Health
```bash
python backend/check_backend.py
```

### Rebuild Frontend Cache
```bash
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

### Database Reset (SQLite)
```bash
# Delete SQLite database
rm backend/sql_app.db

# Backend will recreate on next start
```

---

## Help & Support

If you're still having issues:

1. **Check logs** in the terminal windows
2. **Verify connectivity**: `curl http://localhost:8000/health`
3. **Clear browser cache**: Ctrl+Shift+Delete
4. **Restart both servers**: Close and run again

---

**Status**: ✅ Ready to Launch
Last Updated: April 14, 2026
