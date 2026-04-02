# 🚀 Production Deployment Roadmap: AxionX (ProjectPilot)

This plan outlines the steps required to transition the ProjectPilot full-stack application from its current local development state to a secure, scalable, and production-ready website.

## 🏗️ 1. Infrastructure & Platform Selection

To ensure high performance and low cost, we will use the following industry-standard platforms:

| Component | Recommended Platform | Reason |
| :--- | :--- | :--- |
| **Frontend (Next.js)** | **Vercel** | Native support for Next.js features, edge caching, and automated CI/CD. |
| **Backend (FastAPI)** | **Render.com** or **Railway** | Excellent Python support with easy environment variable management and auto-scaling. |
| **Database (PostgreSQL)**| **Supabase** or **Neon** | Managed PostgreSQL with connection pooling and generous free tiers. |
| **Mailing Service** | **Gmail SMTP** | Already implemented; requires an "App Password" for production. |
| **Storage (Static Files)**| **AWS S3** or **Cloudinary** | (Optional) If you plan to store generated ZIPs/PDFs persistently instead of ephemeral server storage. |

---

## 🛠️ 2. Backend Hardening (Python/FastAPI)

### ✅ Essential Dependency Updates
The current `requirements.txt` is missing critical production packages.
- [ ] **Add Database Drivers**: `psycopg2-binary` for PostgreSQL connection.
- [ ] **Add Production Server**: `gunicorn` (process manager for Uvicorn).
- [ ] **Add Missing Utils**: `slowapi` (already used in code), `alembic` (for migrations), `httpx` (for async requests).

### ✅ Database Migrations (Reliable Updates)
Stop using `Base.metadata.create_all()` in production as it cannot handle schema changes.
- [ ] Initialize Alembic properly.
- [ ] Create an initial "v1_schema" migration that matches the current production-wanted state.
- [ ] Set up the deployment script to run `alembic upgrade head` on every build.

### ✅ Environment Security
- [ ] **SECRET_KEY**: Ensure a 64-character hex key is generated and stored in production envs.
- [ ] **ALLOWED_ORIGINS**: Set this strictly to your production frontend URL (e.g., `https://your-domain.com`).
- [ ] **DEBUG/ENV**: Ensure `ENV=production` is set to disable Swagger/Redoc and enable strict security headers.

---

## 🎨 3. Frontend Optimization (Next.js)

### ✅ Environment Management
- [ ] Set `NEXT_PUBLIC_API_URL` in Vercel to point to your Render/Railway backend.
- [ ] Verify that all `fetch` calls use this base URL (currently correctly implemented in `api.ts`).

### ✅ Visual & SEO Polish
- [ ] **Dynamic Titles/Meta**: Update `layout.tsx` and page components with SEO-optimized titles and descriptions.
- [ ] **Web Vitals**: Check image components for `alt` tags and proper sizing (Standard Next.js components).
- [ ] **Error Handling**: Add a global `error.tsx` and `not-found.tsx` to handle unexpected crashes gracefully.

### ✅ Production Build Check
- [ ] Run `npm run build` locally in the `frontend` directory to catch any TypeScript errors or linting violations before pushing.

---

## 🚢 4. Deployment Playbook (Step-by-Step)

### Step 1: Provision the Database
1. Create a project on **Supabase**.
2. Get the **PostgreSQL Connection String**.
3. Add it to your backend environment as `DATABASE_URL`.

### Step 2: Deploy the Backend
1. Connect GitHub repository to **Render/Railway**.
2. Set Build Command: `pip install -r backend/requirements.txt`
3. Set Start Command: `gunicorn -k uvicorn.workers.UvicornWorker backend.app.main:app`
4. Add all environment variables (Database, SEO, Email, Secret Key).

### Step 3: Deploy the Frontend
1. Connect GitHub repository to **Vercel**.
2. Set Root Directory to `frontend`.
3. Add `NEXT_PUBLIC_API_URL` pointing to your Backend URL.

---

## 🩺 5. Post-Deployment Audit
- [ ] Verify OTP email delivery from the production server.
- [ ] Test the full registration-to-project-generation flow.
- [ ] Check CORS headers in the browser console for any "Access-Control-Allow-Origin" errors.
- [ ] Confirm database entries are being created in the remote PostgreSQL instance.
