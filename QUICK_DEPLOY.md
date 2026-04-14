# 🚀 Quick Deployment Guide

## Pre-Deployment Checklist

✅ Smooth scrolling enabled
✅ Image optimization configured
✅ Production build optimized
✅ Performance metrics ready for monitoring

## 5-Minute Quick Start

### 1. Prepare Frontend
```bash
cd frontend

# Copy environment template
cp .env.example .env.local

# Edit .env.local with your values
# NEXT_PUBLIC_API_URL=your-backend-url
# NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
# NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY=your-key
```

### 2. Prepare Backend
```bash
cd backend

# Ensure .env has production values
# ENV=production
# DATABASE_URL=your-production-db
# ALLOWED_ORIGINS=your-frontend-domain
```

### 3. Test Locally
```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Browser: http://localhost:3000
# Verify smooth scrolling, all pages load, no console errors
```

### 4. Build Production
```bash
cd frontend
npm run build
npm run start

# Check that:
# - No build errors
# - .next folder created
# - App loads at http://localhost:3000
```

## Deploy to Vercel (1 Click)

1. Push to GitHub: `git push origin main`
2. Go to vercel.com/new
3. Import your repository
4. Set Root Directory: `frontend`
5. Add Environment Variables:
   - `NEXT_PUBLIC_API_URL`
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY`
6. Click Deploy

**Done!** Your app is live in seconds.

## Deploy to Railway

1. Go to railway.app
2. Create new project → GitHub
3. Select your repository
4. Add variables (same as Vercel)
5. Configure build: `npm run build` (frontend folder)
6. Railway detects Next.js automatically
7. Deploy

## Deploy Backend to Render

1. Go to render.com
2. Create new Web Service
3. Connect GitHub
4. Select backend directory
5. Build: `pip install -r requirements.txt`
6. Start: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
7. Add environment variables
8. Deploy

## Docker Deployment

```bash
# Build
docker build -t myapp .

# Run
docker run -p 3000:3000 myapp

# Push to registry
docker tag myapp myregistry/myapp
docker push myregistry/myapp
```

## Performance Tips

### Already Optimized:
- ✅ Smooth scrolling on all pages
- ✅ Image optimization (WebP/AVIF)
- ✅ Code splitting
- ✅ SWC minification
- ✅ Font optimization (display: swap)
- ✅ CSS optimization
- ✅ Cache headers configured

### Further Optimization:
```bash
# Run Lighthouse audit
npm run build
npm run start
# Open DevTools → Lighthouse → Generate Report

# Target scores:
# Performance: > 90
# Accessibility: > 90
# Best Practices: > 90
# SEO: > 90
```

## Monitoring After Deployment

### Check Health
```bash
# Backend
curl https://your-backend.com/health

# Frontend
curl https://your-frontend.com/ -I

# Monitor logs
# Vercel: Dashboard > Deployments > Logs
```

### Common Issues & Fixes

**Issue**: Smooth scrolling not working
- Solution: Clear browser cache, check CSS loaded

**Issue**: API calls failing
- Solution: Check NEXT_PUBLIC_API_URL environment variable

**Issue**: Images not loading
- Solution: Verify image paths relative to public folder

**Issue**: Build too slow
- Solution: Check node_modules size, run `npm prune`

## Security Checklist

Before going live:
- [ ] All secrets in environment variables
- [ ] No API keys in code
- [ ] HTTPS enabled (auto with Vercel/Railway)
- [ ] CORS configured for your domain
- [ ] Rate limiting on backend
- [ ] Error messages don't expose internals
- [ ] Database access restricted

```bash
# Scan for secrets
npm install -g git-secrets
git secrets --scan
```

## Rollback if Issues

### Vercel
1. Dashboard → Deployments
2. Find previous deployment
3. Click "Promote to Production"

### Railway
1. Go to deployment history
2. Click previous working version
3. Redeploy

### Manual
```bash
git revert <commit-hash>
git push
# 60 seconds later: live again
```

## Next Steps

1. Read [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions
2. Check [PERFORMANCE_OPTIMIZATION.md](PERFORMANCE_OPTIMIZATION.md) for metrics
3. Set up monitoring on your deployment platform
4. Configure custom domain
5. Enable Sentry for error tracking (optional)

## Support

- [Full Deployment Guide](DEPLOYMENT.md)
- [Performance Metrics](PERFORMANCE_OPTIMIZATION.md)
- [Project README](README.md)

---

**Questions?** Check the troubleshooting section in DEPLOYMENT.md
