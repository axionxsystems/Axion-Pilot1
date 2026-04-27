# 🚀 Manual Deployment Tasks: AxionX (ProjectPilot)

I have successfully prepared the codebase for deployment. I've updated your dependencies, fixed TypeScript build errors, and generated the necessary Alembic migration scripts. 

Now, you have to perform these **manual steps** on the platforms to bring the website live.

## 🗄️ Step 1: Create the Production Database (Supabase)

You need a remote PostgreSQL database to store users and generated projects.
1. Go to [Supabase](https://supabase.com/) and create a free account if you don't have one.
2. Click **New Project** and select your organization.
3. Name it "AxionX" and generate a strong database password (save this password!).
4. Choose the region closest to your users.
5. Once the project is provisioned (takes ~2 minutes), go to **Project Settings -> Database**.
6. Scroll down to **Connection String -> URI** and copy the string. 
7. **Important**: Replace `[YOUR-PASSWORD]` in the string with the actual password you generated in step 3. This string is your `DATABASE_URL`.

---

## ⚙️ Step 2: Deploy the Backend (Render.com)

Render is great for containerless Python applications.
1. Push your latest code (including the changes I just made) to a **GitHub repository**.
2. Go to [Render.com](https://render.com/) and log in with GitHub.
3. Click **New -> Web Service** and select **Build and deploy from a Git repository**.
4. Connect the GitHub repository containing this project.
5. Fill out the configuration:
   * **Name**: `axionx-backend`
   * **Root Directory**: `backend` (This is crucial!)
   * **Runtime**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `alembic upgrade head && gunicorn -k uvicorn.workers.UvicornWorker app.main:app`
6. Scroll down to **Environment Variables** and add the following:
   * `DATABASE_URL`: *(Paste the Supabase URI from Step 1)*
   * `SECRET_KEY`: *(Generate a secure string, e.g., `axionx-prod-secret-994x-secure`)*
   * `ENV`: `production`
   * `EMAIL_USER`: *(Your Gmail address)*
   * `EMAIL_PASS`: *(Your Gmail App Password)*
   * `GEMINI_API_KEY`: *(Your Gemini API key from key.txt)*
   * `ALLOWED_ORIGINS`: `*` *(For now, until Vercel is live. Once Vercel gives you a domain, change this to your Vercel URL).*
7. Click **Create Web Service**. Wait for the build to finish. Once live, copy the Render URL (e.g., `https://axionx-backend-xxxx.onrender.com`).

---

## 🌐 Step 3: Deploy the Frontend (Vercel)

Vercel will host your Next.js frontend application.
1. Go to [Vercel](https://vercel.com/) and log in with GitHub.
2. Click **Add New -> Project**.
3. Import the same GitHub repository.
4. Fill out the configuration:
   * **Project Name**: `axionx`
   * **Framework Preset**: `Next.js`
   * **Root Directory**: Click "Edit" and select the `frontend` folder.
5. Open the **Environment Variables** section and add:
   * `NEXT_PUBLIC_API_URL`: *(Paste the Render URL from Step 2, and add `/api` at the end! Example: `https://axionx-backend-xxxx.onrender.com/api`)*
6. Click **Deploy**. Vercel will build and launch your application.
7. Once finished, click **Continue to Dashboard** and visit your shiny new custom domain!

---

## 🔒 Final Security Step

Once Vercel gives you your frontend URL (e.g., `https://axionx.vercel.app`), go back to your Render backend:
1. Open the **Environment Variables** tab.
2. Modify `ALLOWED_ORIGINS` to be exactly your Vercel URL: `https://axionx.vercel.app` (no trailing slash).
3. This ensures hackers cannot use your backend API from other websites.
