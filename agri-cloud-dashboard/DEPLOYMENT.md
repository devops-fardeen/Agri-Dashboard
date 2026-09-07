# 🚀 Deploying AgriSmart Cloud Dashboard to Vercel

Follow these straightforward steps to deploy your live Next.js Cloud Dashboard to Vercel with automatic HTTPS, global CDN, and continuous GitHub deployment.

---

## 📋 Option A: Deploy via GitHub (Recommended)

1. **Commit and push your latest code to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy: Updated unified auth, 7-day weather widget, and alerts hub"
   git push origin main
   ```

2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com) and log in with GitHub.
   - Click **"Add New..."** ➔ **"Project"**.
   - Select your repository: `Agri-Dashboard`.

3. **Configure Project Settings**:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: Click `Edit` and select `agri-cloud-dashboard`.
   - **Build Command**: `npm run build` (Default)
   - **Output Directory**: `.next` (Default)
   - **Install Command**: `npm install` (Default)

4. **Add Environment Variables**:
   In the **Environment Variables** section, add the following key-value pairs:

   | Variable Name | Description | Example / Current Value |
   | :--- | :--- | :--- |
   | `MONGODB_URI` | MongoDB Atlas Connection String | `mongodb+srv://...` (From your `.env.local`) |
   | `BETTER_AUTH_SECRET` | 32-char Cryptographic Secret | `a_random_32_character_secret_key_sih2026` |
   | `BETTER_AUTH_URL` | Your Production Vercel Domain | `https://your-project.vercel.app` |
   | `GOOGLE_CLIENT_ID` | Google OAuth Client ID | `your-google-client-id.apps.googleusercontent.com` |
   | `GOOGLE_CLIENT_SECRET` | Google OAuth Secret | `your-google-client-secret` |
   | `EDGE_SYNC_API_KEY` | Edge Station Sync Auth Token | `dashboard@agri1` |

5. **Click "Deploy"**:
   - Vercel will build and assign you a live HTTPS domain (e.g., `https://agri-smart-dashboard.vercel.app`).

---

## ⚡ Option B: Direct Terminal Deployment via Vercel CLI

In your terminal, navigate into `agri-cloud-dashboard` and run:

```bash
cd agri-cloud-dashboard
npx vercel
```

- Follow the interactive prompts (log in with your browser / GitHub, accept default project settings).
- To deploy to production:
  ```bash
  npx vercel --prod
  ```

---

## 🔒 Post-Deployment Checklist

### 1. Google OAuth Callback URL
In your [Google Cloud Console](https://console.cloud.google.com/apis/credentials):
- Under **Authorized redirect URIs**, add:
  - `https://<your-project>.vercel.app/api/auth/callback/google`
- Under **Authorized JavaScript origins**, add:
  - `https://<your-project>.vercel.app`

### 2. Update Raspberry Pi Edge Sync Destination
In `agri-edge-station/sync_worker.py` (or your edge `.env`), update the cloud URL to your live Vercel domain:
```python
CLOUD_API_URL = "https://<your-project>.vercel.app/api/telemetry/sync"
```
