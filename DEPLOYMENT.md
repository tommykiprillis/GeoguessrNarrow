# Deployment Guide: GitHub Pages + Render

This guide covers deploying the frontend to GitHub Pages and the backend to Render (free tier).

---

## Part 1: Deploy Backend to Render

### 1. Prepare Repository
- Ensure `.env` is in `.gitignore` ✓
- Commit and push to GitHub:
  ```bash
  git add .
  git commit -m "Add deployment configuration"
  git push origin main
  ```

### 2. Create Render Account
- Go to [render.com](https://render.com)
- Sign up with GitHub account
- Authorize Render to access your repositories

### 3. Deploy on Render
1. Click "New +"
2. Select "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `geoguessr-narrower` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.app:app --host 0.0.0.0 --port $PORT`
   - **Region**: Choose closest to you
5. Click "Create Web Service"

### 4. Get Your Backend URL
- Once deployed, Render provides a URL like: `https://geoguessr-narrower.onrender.com`
- Copy this URL (you'll need it for the frontend)

---

## Part 2: Deploy Frontend to GitHub Pages

### 1. Create GitHub Pages Repository
- Create a new repository named `username.github.io` (replace `username` with your GitHub username)
- This will automatically be your GitHub Pages site

### 2. Update Frontend Configuration
In `src/script.js`, update line 10:
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? window.location.origin
  : 'https://YOUR-RENDER-URL.onrender.com'; // Add your Render URL here
```

Example:
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? window.location.origin
  : 'https://geoguessr-narrower.onrender.com';
```

### 3. Copy Frontend Files to GitHub Pages Repository
Copy these files to your `username.github.io` repository:
- `src/index.html` → root
- `src/script.js` → root
- `src/styles.css` → root  
- `data/features.json` → root
- `data/countries.json` → root

### 4. Push to GitHub Pages
```bash
cd /path/to/username.github.io
git add .
git commit -m "Deploy GeoGuessr Narrower"
git push origin main
```

### 5. Verify Deployment
- Visit `https://username.github.io` in your browser
- It should load and work with your Render backend

---

## Part 3: Testing

### Local Testing
```bash
# Terminal 1: Backend
uvicorn src.app:app --reload

# Terminal 2: Frontend (serve static files)
# Open src/index.html in browser or use a simple HTTP server
python -m http.server 8001  # Different port to avoid conflict
```

### Production Testing
1. Visit your GitHub Pages URL
2. Try selecting features
3. Click "Find Countries" and verify results

---

## Troubleshooting

### CORS Errors
- Backend has CORS enabled for all origins
- Check browser console for exact error message
- Ensure API_BASE_URL in script.js is correct

### Features/Countries Not Loading
- Check Render backend status (visit `https://your-url.onrender.com/test`)
- Verify data files exist in Render deployment
- Check Render logs for errors

### Backend Sleeping (Free Tier)
- Render's free tier spins down inactive services
- May take 30 seconds to wake up on first request
- Consider upgrading to avoid cold starts

---

## Future Updates

When you update the code:
1. **Backend changes**: Push to GitHub; Render auto-deploys
2. **Frontend changes**: 
   - Update `username.github.io` repo
   - Push to GitHub; GitHub Pages auto-deploys

---

## Environment Variables

Currently not needed, but if you add sensitive config later:
1. Add to `.env.example` with placeholder
2. Never commit `.env`
3. In Render: Settings → Environment add your real values
