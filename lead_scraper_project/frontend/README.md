# 🚀 LeadScout AI: Vercel Deployment Guide

This directory (`/frontend`) contains the Next.js 15 showcase application carefully engineered to be deployed directly to Vercel. Since standard Python automation libraries like Playwright cannot run inside Vercel's lightweight serverless functions, this frontend acts as your **Premium Product Showcase and Interactive Demo** for your portfolio, investors, and clients.

## 🌍 How to Deploy to Vercel Instantly

You do not need to deploy the heavy Python backend. Vercel is meant for frontends. Follow these steps to get your live URL in 3 minutes:

### 1. Push to GitHub
If you haven't already, push this entire project to a GitHub repository.
```bash
git init
git add .
git commit -m "Initial commit with Vercel frontend"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### 2. Connect to Vercel
1. Go to [Vercel.com](https://vercel.com/) and log in with your GitHub account.
2. Click **Add New Project**.
3. Select your GitHub repository from the list and click **Import**.

### 3. Configure the Build Settings (CRITICAL)
Since you have a Python backend in the root and the Next.js app in the `frontend` folder, you MUST tell Vercel where the web app lives.

- **Framework Preset**: Next.js
- **Root Directory**: `frontend`  <-- *Crucial step! Click Edit and select the frontend folder.*
- **Build Command**: `Next.js default` (leave blank)
- **Install Command**: `Next.js default` (leave blank)

### 4. Deploy!
Click the big **Deploy** button. Vercel will build the Tailwind UI and assign you an instant live URL (e.g., `https://leadscout-ai.vercel.app`).

---

## 📸 What this solves for you
By deploying this Next.js showcase, you immediately have a fast, globally distributed URL that you can attach to your LinkedIn, Resume, and Pitch Decks to visually prove the power of the **D-AEDSA Algorithm** without forcing reviewers to install Python and Playwright locally.
