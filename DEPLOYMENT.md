# Deployment Guide

## Pre-Deployment Performance Optimizations

### Frontend Optimizations Applied ✅
- **Smooth Scrolling**: Enabled globally across all pages
- **Image Optimization**: WebP & AVIF formats configured
- **Code Splitting**: Automatic with Next.js
- **SWC Minification**: Production-ready compilation
- **Performance Monitoring**: Ready for analytics

## 1. Backend (FastAPI)

### Deploy on Render.com / Railway / Fly.io

1.  **Repository Setup**: Push your code to GitHub.
2.  **Environment Variables**:
    *   `GROQ_API_KEY`: Your Groq API Key.
    *   `OPENROUTER_API_KEY`: (Optional) If using OpenRouter.
    *   `ENV`: Set to `production`
    *   `ALLOWED_ORIGINS`: Your frontend domain (e.g., `https://yourapp.com`)
3.  **Build Command**: `pip install -r backend/requirements.txt`
4.  **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port 10000`
    *   *Note*: Ensure you set the Root Directory to `.` or `backend` depending on your repo structure.

### Performance Configuration for Backend
```python
# Add to your FastAPI app for production
app.add_middleware(GZIPMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 2. Frontend (Next.js) - Deployment Ready

### Deploy on Vercel (Recommended)

1.  **Import Project**: Select your GitHub repo in Vercel.
2.  **Root Directory**: Set to `frontend`.
3.  **Framework Preset**: Select Next.js.
4.  **Build Command**: `npm run build`
5.  **Environment Variables**:
    *   `NEXT_PUBLIC_API_URL`: The URL of your deployed Backend (e.g., `https://my-backend.onrender.com/api`)
    *   `NEXT_PUBLIC_SUPABASE_URL`: Your Supabase URL
    *   `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY`: Your Supabase key
6.  **Deploy**: Click Deploy.

### Deploy using Docker

**Dockerfile** (in root or frontend directory):
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
RUN npm install -g next

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./

EXPOSE 3000
CMD ["npm", "start"]
```

### Deploy on Other Platforms

**Railway.app**
1. Connect your GitHub repo
2. Select `frontend` as root directory
3. Set environment variables
4. Deploy automatically

**Netlify**
1. Connect GitHub repo
2. Build command: `npm run build`
3. Publish directory: `.next`
4. Set environment variables

## Local Development

**Backend**:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

## Environment Variables Setup

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=https://your-api.example.com
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY=your-key
NODE_ENV=production
```

### Backend (.env)
```env
ENV=production
DATABASE_URL=postgresql://user:password@host:port/db
SECRET_KEY=your-long-secret-key
ALLOWED_ORIGINS=https://yourapp.com,https://www.yourapp.com
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
GROQ_API_KEY=your-groq-key
GEMINI_API_KEY=your-gemini-key
PASSKEY_ORIGIN=https://yourapp.com
PASSKEY_RP_ID=yourapp.com
```

## Performance Testing

### Frontend Lighthouse Audit
```bash
# In frontend directory
npm run build
npm run start
# Open http://localhost:3000 and run Lighthouse in Chrome DevTools
```

### Load Testing
```bash
# Using Apache Bench
ab -n 1000 -c 10 https://your-api.example.com/health

# Using curl for quick tests
curl -w "@curl-format.txt" -o /dev/null -s https://your-api.example.com/
```

## Security Checklist ✅

- [ ] All API keys in environment variables
- [ ] HTTPS enabled on all domains
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Database credentials rotated
- [ ] Console logs removed from production
- [ ] Error tracking setup (Sentry)
- [ ] Monitoring and alerts configured

## Production Deployment Steps

### 1. Frontend
```bash
cd frontend
npm install
npm run build
npm run start
# Or use: npm run export (for static exports)
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
# Or: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Verify Deployment
- Frontend: Test all pages load smoothly
- Backend: Check API endpoints respond
- Smooth scrolling: Verify on mobile and desktop
- Performance: Run Lighthouse audit

## Rollback Plan

If issues occur:
```bash
# Git rollback
git revert <commit-hash>
git push

# Or use platform-specific rollback:
# Vercel: Dashboard > Deployments > Revert
# Railway: Previous deployment version
```

## Monitoring & Logs

### Vercel
- Access logs: Dashboard > Deployments > Logs
- Realtime monitoring: Vercel Analytics

### Self-hosted
```bash
# Check backend logs
tail -f backend.log

# Monitor frontend
# Check browser console and network tab
```

## Support

- Check [RESUME_POINTS.md](RESUME_POINTS.md) for development notes
- See [README.md](README.md) for feature documentation
- Review error logs during deployment issues
