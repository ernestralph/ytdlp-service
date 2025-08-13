# yt-dlp API Service

A simple Flask API service that wraps yt-dlp for downloading YouTube audio.

## Quick Deploy to Railway

1. Create account at [Railway.app](https://railway.app)
2. Click "Deploy from GitHub"
3. Connect this repository
4. Set environment variables:
   - `API_KEY=your-secret-key-123` (optional)
5. Deploy!

## Quick Deploy to Render

1. Create account at [Render.com](https://render.com)
2. Create new "Web Service"
3. Connect this repository
4. Set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Environment: `API_KEY=your-secret-key-123`

## Local Testing

```bash
cd ytdlp-service
pip install -r requirements.txt
python app.py
```

Test with:
```bash
curl -X POST http://localhost:8080/download \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-key-123" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}' \
  --output audio.webm
```

## Usage in Your App

After deployment, add to your environment:
```env
YTDLP_API_URL=https://your-service.railway.app
YTDLP_API_KEY=your-secret-key-123
```
