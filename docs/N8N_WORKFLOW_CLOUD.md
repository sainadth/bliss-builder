# Bliss Builder N8N Cloud Workflow - Complete Guide

## 📖 What This Document Is

This guide shows you how to build a **fully cloud-based** ASMR video automation system using N8N Cloud (no local computer required after setup).

**What it does**:
1. Finds trending ASMR videos every day (via cloud API)
2. Uses AI to create an ASMR theme
3. Generates an 8-second video using Google's Veo 3
4. Automatically uploads to YouTube

**Cost**: $27-33/month (all cloud services)  
**Manual work**: Zero after setup  
**Local computer**: Not needed (runs 24/7 in cloud)

---

## 🎯 ARCHITECTURE OVERVIEW

### Cloud-Native Workflow

```
┌─────────────────────────────────────────────┐
│   N8N CLOUD (yourname.app.n8n.cloud)        │
│                                             │
│   ┌─────────────────────────────────────┐   │
│   │ 1. Schedule Trigger (3 PM daily)    │   │
│   └────────────┬────────────────────────┘   │
│                │                            │
│                ▼                            │
│   ┌─────────────────────────────────────┐   │
│   │ 2. HTTP Request → Trend API         │───┼──→ Vercel/Railway
│   │    GET /fetch-asmr-trends           │   │   (FastAPI Service)
│   └────────────┬────────────────────────┘   │
│                │                            │
│                ▼                            │
│   ┌─────────────────────────────────────┐   │
│   │ 3. HTTP Request → Groq API          │───┼──→ Groq (Theme)
│   │    Extract ASMR theme               │   │
│   └────────────┬────────────────────────┘   │
│                │                            │
│                ▼                            │
│   ┌─────────────────────────────────────┐   │
│   │ 4. HTTP Request → Groq API          │───┼──→ Groq (Narration)
│   │    Generate video narration         │   │
│   └────────────┬────────────────────────┘   │
│                │                            │
│                ▼                            │
│   ┌─────────────────────────────────────┐   │
│   │ 5. HTTP Request → Veo 3 API         │───┼──→ Google Veo 3
│   │    Generate 8s video (with polling) │   │
│   └────────────┬────────────────────────┘   │
│                │                            │
│                ▼                            │
│   ┌─────────────────────────────────────┐   │
│   │ 6. HTTP Request → YouTube API       │───┼──→ YouTube
│   │    Upload video as Short            │   │
│   └────────────┬────────────────────────┘   │
│                │                            │
│                ▼                            │
│   ┌─────────────────────────────────────┐   │
│   │ 7. Google Sheets → Log result       │───┼──→ Google Sheets
│   └─────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 📋 PREREQUISITES

### 1. Accounts Needed (All Cloud-Based)
- [ ] **N8N Cloud** account (https://n8n.io) - $24/month after trial
- [ ] **Google Cloud** account (YouTube API + Gemini/Veo 3)
- [ ] **Groq** account (free tier for AI)
- [ ] **Vercel** or **Railway** account (free tier for API hosting)
- [ ] **YouTube** channel (for uploads)

### 2. No Local Computer Required
- Entire workflow runs in the cloud
- You only need a browser to set everything up
- Can monitor from phone/tablet after setup

---

## 🚀 SETUP GUIDE

### PART 1: Deploy Trend-Fetching API (30 minutes)

Since N8N Cloud doesn't support `Execute Command`, we need a cloud API endpoint.

#### Option A: Deploy to Vercel (Recommended)

**Step 1.1: Create the API**

1. Go to https://github.com/new
2. Create new repository: `asmr-trend-api`
3. Click "Upload files"
4. Create file: `api/trends.py`

```python
#filepath: api/trends.py
from http.server import BaseHTTPRequestHandler
import json
import os
from googleapiclient.discovery import build

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Get YouTube API key from environment
        api_key = os.environ.get('YOUTUBE_API_KEY')
        if not api_key:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "API key not configured"}).encode())
            return
        
        try:
            # Fetch ASMR trending videos
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # Search for ASMR videos
            request = youtube.search().list(
                part='snippet',
                q='ASMR',
                type='video',
                order='viewCount',
                maxResults=50,
                relevanceLanguage='en',
                safeSearch='strict'
            )
            response = request.execute()
            
            # Format results
            trends = []
            for item in response.get('items', []):
                snippet = item.get('snippet', {})
                trends.append({
                    "video_id": item['id'].get('videoId'),
                    "title": snippet.get('title'),
                    "description": snippet.get('description', '')[:200],
                    "channel": snippet.get('channelTitle'),
                    "published_at": snippet.get('publishedAt')
                })
            
            # Return JSON
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(trends).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
```

5. Create file: `requirements.txt`
```
google-api-python-client==2.108.0
```

6. Create file: `vercel.json`
```json
{
  "functions": {
    "api/trends.py": {
      "runtime": "python3.9"
    }
  }
}
```

**Step 1.2: Deploy to Vercel**

1. Go to https://vercel.com/new
2. Import your `asmr-trend-api` repository
3. Add Environment Variable:
   - Name: `YOUTUBE_API_KEY`
   - Value: (your YouTube API key)
4. Click "Deploy"
5. Copy your API URL: `https://asmr-trend-api.vercel.app/api/trends`

#### Option B: Deploy to Railway (Alternative)

Similar process but uses Railway's Python environment.

---

### PART 2: Set Up APIs (45 minutes)

#### Step 2.1: YouTube Data API

(Same as original guide - Steps 1-8 from PROJECT_PROPOSAL.md)

#### Step 2.2: Gemini API

(Same as original guide)

#### Step 2.3: Groq API

(Same as original guide)

---

### PART 3: Build N8N Cloud Workflow (90 minutes)

#### Step 3.1: Create Workflow

1. Log in to N8N Cloud: `https://yourname.app.n8n.cloud`
2. Click "New Workflow"
3. Name it: `ASMR Daily Automation`

#### Step 3.2: Add Nodes (HTTP-Based)

**Node 1: Schedule Trigger**
- Type: Schedule Trigger
- Mode: Custom
- Cron Expression: `0 15 * * *` (3 PM daily)
- Timezone: Your timezone

**Node 2: HTTP Request - Fetch Trends**
- Type: HTTP Request
- Method: GET
- URL: `https://your-api.vercel.app/api/trends`
- Response Format: JSON
- Test the node (should return 50 ASMR videos)

**Node 3: Code - Format Trends for LLM**
```javascript
// Format top 15 trends for theme extraction
const trends = $input.first().json;
const top15 = trends.slice(0, 15);
const formatted = top15.map(t => 
  `- ${t.title}\n  Description: ${t.description}`
).join('\n\n');

return [{json: {trendsPrompt: formatted, allTrends: trends}}];
```

**Node 4: HTTP Request - Extract Theme (Groq)**
- Method: POST
- URL: `https://api.groq.com/openai/v1/chat/completions`
- Authentication: Header Auth
  - Name: `Authorization`
  - Value: `Bearer {{$credentials.groqApi}}`
- Body (JSON):
```json
{
  "model": "llama-3.1-70b-versatile",
  "messages": [
    {
      "role": "system",
      "content": "You are an ASMR expert. Extract ONE concise ASMR theme (6-14 words) from the following trending videos. Be brand-safe and peaceful. Output ONLY the theme."
    },
    {
      "role": "user",
      "content": "={{$json.trendsPrompt}}"
    }
  ],
  "max_tokens": 100,
  "temperature": 0.4
}
```

**Node 5: Set - Store Theme**
```javascript
return [{
  json: {
    theme: $json.choices[0].message.content.trim(),
    allTrends: $node["Code - Format Trends"].json.allTrends
  }
}];
```

**Node 6: HTTP Request - Generate Narration (Groq)**
- Method: POST
- URL: `https://api.groq.com/openai/v1/chat/completions`
- Body:
```json
{
  "model": "llama-3.1-70b-versatile",
  "messages": [
    {
      "role": "system",
      "content": "You are an ASMR video director. Create a detailed 2-3 sentence narration for an 8-second ASMR video. Include sensory details, calming visuals, portrait format (1080x1920). Be brand-safe."
    },
    {
      "role": "user",
      "content": "Theme: ={{$json.theme}}"
    }
  ],
  "max_tokens": 250,
  "temperature": 0.7
}
```

**Node 7: Set - Store Narration**
```javascript
return [{
  json: {
    theme: $node["Set - Store Theme"].json.theme,
    narration: $json.choices[0].message.content.trim()
  }
}];
```

**Node 8: HTTP Request - Generate Video (Veo 3)**

⚠️ **Note**: Veo 3 requires polling. You have two options:

**Option A: Direct API Call (Advanced)**
```javascript
// This requires handling polling in workflow
// See full implementation below
```

**Option B: Use Wrapper Service (Recommended)**
- Deploy a Veo 3 polling service to Railway
- Endpoint handles polling internally
- Returns video URL when ready

**Node 9: HTTP Request - Download Video**
- Method: GET
- URL: `={{$json.videoUrl}}` (from Veo 3 response)
- Response Format: File
- Store binary data

**Node 10: HTTP Request - Upload to YouTube**
- Method: POST
- URL: `https://www.googleapis.com/upload/youtube/v3/videos?uploadType=multipart&part=snippet,status`
- Authentication: OAuth2 (YouTube)
- Body Content Type: Multipart
- Parts:
  1. JSON metadata (snippet)
  2. Binary video data

**Node 11: Google Sheets - Log Result**
- Operation: Append
- Spreadsheet: Your log sheet
- Values:
  - Timestamp: `={{$now}}`
  - Theme: `={{$node["Set - Store Theme"].json.theme}}`
  - Video ID: `={{$json.id}}`
  - Status: `success`

---

### PART 4: Handle Veo 3 Polling (Advanced)

Since Veo 3 requires polling, you need a wrapper service:

#### Deploy Veo 3 Wrapper to Railway

```python
# filepath: veo3_wrapper/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time
from google import genai

app = FastAPI()

class VideoRequest(BaseModel):
    narration: str
    api_key: str
    duration: int = 8

@app.post("/generate-video")
async def generate_video(req: VideoRequest):
    try:
        client = genai.Client(api_key=req.api_key)
        
        # Start video generation
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=f"{req.narration} Duration: {req.duration}s. Format: 1080x1920 portrait."
        )
        
        # Poll until complete (max 10 minutes)
        for i in range(60):
            if operation.done:
                break
            time.sleep(10)
            operation = client.operations.get(operation)
        
        if not operation.done:
            raise HTTPException(status_code=408, detail="Timeout")
        
        # Download video
        video = operation.response.generated_videos[0]
        client.files.download(file=video.video)
        
        # Upload to temporary storage and return URL
        # (Or return base64-encoded video)
        video_url = upload_to_storage(video.video)
        
        return {"video_url": video_url, "status": "complete"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

Deploy to Railway:
1. `railway init`
2. `railway up`
3. Get URL: `https://your-veo3-wrapper.up.railway.app`

---

## 💰 COST BREAKDOWN (Cloud-Only)

| Service | Cost |
|---------|------|
| **N8N Cloud** | $24/month (Starter plan) |
| **Vercel** (Trend API) | Free (hobby tier) |
| **Railway** (Veo 3 wrapper) | Free tier or $5/month |
| **Groq API** | Free (30 req/min) |
| **Google Veo 3** | $3-9/month (~$0.10-0.30/video) |
| **YouTube API** | Free |
| **Google Sheets** | Free |
| **Total** | **$27-38/month** |

---

## 🎉 ADVANTAGES OF CLOUD SETUP

✅ **No local computer needed** - Runs 24/7 in cloud  
✅ **99.9% uptime** - Professional infrastructure  
✅ **Access from anywhere** - Phone, tablet, laptop  
✅ **Automatic scaling** - Handles traffic spikes  
✅ **Easy monitoring** - N8N Cloud dashboard  
✅ **No maintenance** - Cloud services handle updates  

---

## 📞 NEXT STEPS

1. Deploy trend API to Vercel (30 min)
2. Set up N8N Cloud workflow (90 min)
3. Deploy Veo 3 wrapper to Railway (45 min)
4. Test end-to-end (30 min)
5. Enable daily schedule
6. Monitor for first week

---

**Last Updated**: 2025-01-29  
**Version**: 2.0 (Cloud Edition)
