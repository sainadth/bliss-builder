# Bliss Builder - N8N Cloud Only Implementation

## 📖 Overview

This guide implements the **entire Bliss Builder pipeline using N8N Cloud exclusively** - no local Python scripts, no local computer required after setup.

**What runs in N8N Cloud**:
1. Fetch ASMR trends via HTTP Request to YouTube API
2. Extract theme via HTTP Request to Groq API
3. Generate narration via HTTP Request to Groq API
4. Generate video via HTTP Request to Gemini Veo 3 API (with polling)
5. Upload to YouTube via HTTP Request
6. Log results to Google Sheets

**Cost**: $27-33/month  
**Local Computer**: Not needed (100% cloud-based)

---

## 🏗️ ARCHITECTURE

```
┌──────────────────────────────────────────────────┐
│         N8N CLOUD WORKFLOW                       │
│  (runs 24/7 at app.n8n.cloud)                   │
│                                                  │
│  1. Schedule Trigger (3 PM daily)               │
│           ↓                                      │
│  2. HTTP Request → YouTube Data API             │
│     (Search ASMR videos by viewCount)           │
│           ↓                                      │
│  3. Code Node → Filter & Format Results         │
│           ↓                                      │
│  4. HTTP Request → Groq API                     │
│     (Extract ASMR theme)                        │
│           ↓                                      │
│  5. HTTP Request → Groq API                     │
│     (Generate video narration)                  │
│           ↓                                      │
│  6. HTTP Request → Gemini Veo 3 API             │
│     (Start video generation)                    │
│           ↓                                      │
│  7. Loop Node → Poll Veo 3 status               │
│     (Check every 10s until complete)            │
│           ↓                                      │
│  8. HTTP Request → Download video               │
│           ↓                                      │
│  9. HTTP Request → YouTube Upload API           │
│     (Multipart upload)                          │
│           ↓                                      │
│  10. Google Sheets → Log result                 │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 📋 PREREQUISITES

### 1. Accounts Needed
- [ ] **N8N Cloud** - Sign up at https://n8n.io ($24/month after trial)
- [ ] **Google Cloud** - For YouTube API + Gemini API
- [ ] **Groq** - For AI theme/narration (free tier)
- [ ] **Google Sheets** - For logging (free)
- [ ] **YouTube Channel** - For uploads

### 2. API Keys to Obtain

| API | Where to Get | Cost |
|-----|--------------|------|
| YouTube Data API | Google Cloud Console | Free |
| Gemini API | Google AI Studio | ~$0.10-0.30/video |
| Groq API | console.groq.com | Free tier |

---

## 🚀 SETUP GUIDE

### PART 1: Get API Keys (30 minutes)

#### Step 1.1: YouTube Data API Key

1. Go to https://console.cloud.google.com/
2. Create project: "Bliss Builder"
3. Enable "YouTube Data API v3"
4. Create credentials:
   - Type: API Key
   - Restrict to: YouTube Data API v3
5. **Copy API Key**: `AIzaSy...`

#### Step 1.2: YouTube OAuth2 (for uploads)

1. In same Google Cloud project
2. Create OAuth 2.0 Client ID:
   - Application type: Web application
   - Authorized redirect URIs: `https://oauth.n8n.cloud/oauth2-credential/callback`
3. Download JSON credentials
4. Save as `youtube_oauth_credentials.json`

#### Step 1.3: Gemini API Key

1. Go to https://aistudio.google.com/app/apikey
2. Create API key for "Bliss Builder" project
3. **Copy API Key**: `AIzaSy...`

#### Step 1.4: Groq API Key

1. Go to https://console.groq.com/
2. Sign up (Google/GitHub)
3. Create API Key: "Bliss Builder"
4. **Copy API Key**: `gsk_...`

---

### PART 2: Configure N8N Cloud (15 minutes)

#### Step 2.1: Add Credentials to N8N

1. Log in to N8N Cloud: `https://yourname.app.n8n.cloud`
2. Go to **Settings → Credentials**

**Add YouTube API Key**:
- Type: Header Auth
- Name: `YouTube-API-Key`
- Header Name: `X-API-Key`
- Header Value: `YOUR_YOUTUBE_API_KEY`

**Add YouTube OAuth2**:
- Type: OAuth2 API
- Name: `YouTube-OAuth2`
- Upload `youtube_oauth_credentials.json`
- Authorize with your YouTube channel

**Add Groq API Key**:
- Type: Header Auth
- Name: `Groq-API`
- Header Name: `Authorization`
- Header Value: `Bearer YOUR_GROQ_API_KEY`

**Add Gemini API Key**:
- Type: Header Auth
- Name: `Gemini-API`
- Header Name: `x-goog-api-key`
- Header Value: `YOUR_GEMINI_API_KEY`

---

### PART 3: Build N8N Workflow (90 minutes)

#### Step 3.1: Create New Workflow

1. In N8N Cloud, click **"New Workflow"**
2. Name: `Bliss Builder - Daily ASMR Shorts`
3. Save workflow

#### Step 3.2: Add Nodes (Complete Configuration)

---

### **Node 1: Schedule Trigger**

- **Type**: Schedule Trigger
- **Settings**:
  - Trigger Times: `Cron`
  - Expression: `0 15 * * *` (3 PM daily)
  - Timezone: Your timezone

**Test**: Click "Execute Node" - should show current timestamp

---

### **Node 2: HTTP Request - Fetch ASMR Trends**

- **Type**: HTTP Request
- **Method**: GET
- **URL**: 
```
https://www.googleapis.com/youtube/v3/search?part=snippet&q=ASMR&type=video&order=viewCount&maxResults=50&relevanceLanguage=en&safeSearch=strict&publishedAfter={{$now.minus(7, 'days').toISO()}}&key={{$credentials.youtubeApiKey}}
```
- **Authentication**: None (API key in URL)
- **Response Format**: JSON

**Test**: Should return 50 ASMR video results

---

### **Node 3: Code - Process Search Results**

- **Type**: Code (JavaScript)
- **Code**:

```javascript
// filepath: Node 3 Code
const items = $input.first().json.items || [];

// Extract video IDs
const videoIds = items.map(item => item.id.videoId).filter(Boolean);

if (videoIds.length === 0) {
  return [{ json: { error: "No videos found" } }];
}

// Prepare for next API call
return [{
  json: {
    videoIds: videoIds.join(','),
    videoCount: videoIds.length
  }
}];
```

---

### **Node 4: HTTP Request - Get Video Details**

- **Type**: HTTP Request
- **Method**: GET
- **URL**:
```
https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={{$json.videoIds}}&key={{$credentials.youtubeApiKey}}
```
- **Response Format**: JSON

**Test**: Returns full video details with tags, view counts

---

### **Node 5: Code - Format Trends for LLM**

- **Type**: Code (JavaScript)
- **Code**:

```javascript
// filepath: Node 5 Code
const videos = $input.first().json.items || [];

// Extract top 15 videos with metadata
const trends = videos.slice(0, 15).map(v => ({
  title: v.snippet.title,
  description: (v.snippet.description || '').substring(0, 200),
  tags: (v.snippet.tags || []).slice(0, 5),
  viewCount: v.statistics.viewCount
}));

// Format for theme extraction prompt
const context = trends.map(t => 
  `Title: ${t.title}\nTags: ${t.tags.join(', ')}`
).join('\n\n');

return [{
  json: {
    trendsContext: context,
    allVideos: videos  // Keep for narration
  }
}];
```

---

### **Node 6: HTTP Request - Extract Theme (Groq)**

- **Type**: HTTP Request
- **Method**: POST
- **URL**: `https://api.groq.com/openai/v1/chat/completions`
- **Authentication**: Header Auth (select `Groq-API`)
- **Body (JSON)**:

```json
{
  "model": "llama-3.1-70b-versatile",
  "messages": [
    {
      "role": "system",
      "content": "You are an ASMR content expert. Extract ONE concise ASMR theme (6-14 words) from trending videos. Be brand-safe, peaceful, imagery-focused. Output ONLY the theme."
    },
    {
      "role": "user",
      "content": "={{$json.trendsContext}}"
    }
  ],
  "max_tokens": 100,
  "temperature": 0.4
}
```

---

### **Node 7: Set - Store Theme**

- **Type**: Set
- **Settings**:
  - **Keep Only Set**: OFF
  - **Values**:
    - `theme`: `={{$json.choices[0].message.content.trim()}}`

---

### **Node 8: HTTP Request - Generate Narration (Groq)**

- **Type**: HTTP Request
- **Method**: POST
- **URL**: `https://api.groq.com/openai/v1/chat/completions`
- **Authentication**: Header Auth (select `Groq-API`)
- **Body (JSON)**:

```json
{
  "model": "llama-3.1-70b-versatile",
  "messages": [
    {
      "role": "system",
      "content": "You are an ASMR video director. Create a detailed 2-3 sentence narration for an 8-second ASMR video. Include sensory details, calming visuals, portrait format (1080x1920). Be brand-safe. Output ONLY the narration."
    },
    {
      "role": "user",
      "content": "Theme: ={{$node['Set - Store Theme'].json.theme}}"
    }
  ],
  "max_tokens": 250,
  "temperature": 0.7
}
```

---

### **Node 9: Set - Store Narration**

- **Type**: Set
- **Values**:
  - `theme`: `={{$node['Set - Store Theme'].json.theme}}`
  - `narration`: `={{$json.choices[0].message.content.trim()}}`

---

### **Node 10: HTTP Request - Start Veo 3 Video Generation**

⚠️ **Important**: This requires Vertex AI authentication (more complex than API key)

**Alternative Simpler Approach**: Use a webhook/serverless function to handle Veo 3 polling

- **Type**: HTTP Request
- **Method**: POST
- **URL**: `https://YOUR_CLOUD_FUNCTION_URL/generate-veo3-video`
- **Body (JSON)**:

```json
{
  "narration": "={{$json.narration}}",
  "theme": "={{$json.theme}}",
  "duration": 8
}
```

**This cloud function handles**:
1. Calling Veo 3 API with proper auth
2. Polling until complete (2-5 minutes)
3. Returning video URL

**Cloud Function Code** (deploy to Google Cloud Functions or Vercel):

```python
# filepath: cloud_function/veo3_handler.py
from google import genai
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/generate-veo3-video', methods=['POST'])
def generate_video():
    data = request.json
    narration = data.get('narration')
    duration = data.get('duration', 8)
    
    client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    
    prompt = f"{narration} Duration: {duration}s. Format: 1080x1920 portrait. Cinematic, peaceful."
    
    operation = client.models.generate_videos(
        model="veo-3.1-generate-preview",
        prompt=prompt
    )
    
    # Poll until done
    for i in range(60):
        if operation.done:
            break
        time.sleep(10)
        operation = client.operations.get(operation)
    
    if not operation.done:
        return jsonify({"error": "Timeout"}), 408
    
    # Get video URL
    video = operation.response.generated_videos[0]
    video_url = upload_to_storage(video)  # Upload to Cloud Storage
    
    return jsonify({"video_url": video_url, "status": "complete"})
```

---

### **Node 11: HTTP Request - Download Video**

- **Type**: HTTP Request
- **Method**: GET
- **URL**: `={{$json.video_url}}`
- **Response Format**: File
- **Binary Property**: `videoData`

---

### **Node 12: HTTP Request - Upload to YouTube**

- **Type**: HTTP Request
- **Method**: POST
- **URL**: `https://www.googleapis.com/upload/youtube/v3/videos?uploadType=media&part=snippet,status`
- **Authentication**: OAuth2 (select `YouTube-OAuth2`)
- **Body Content Type**: Binary Data
- **Binary Data**: `={{$binary.videoData}}`
- **Options**:
  - Add Query Parameters:
    - `uploadType`: `multipart`
    - `part`: `snippet,status`

**Note**: YouTube upload via HTTP in n8n requires multipart handling. Alternative: use YouTube node (if available in n8n Cloud)

---

### **Node 13: Google Sheets - Log Result**

- **Type**: Google Sheets
- **Operation**: Append
- **Authentication**: Google OAuth2
- **Spreadsheet**: Create "ASMR Pipeline Log" sheet
- **Sheet**: Sheet1
- **Columns**:
  - Timestamp: `={{$now}}`
  - Theme: `={{$node['Set - Store Narration'].json.theme}}`
  - Video ID: `={{$json.id}}`
  - Video URL: `=https://youtube.com/shorts/{{$json.id}}`
  - Status: `success`

---

## 🔄 SIMPLIFIED ALTERNATIVE (No Veo 3)

If Veo 3 is too complex, use **text-based video fallback** entirely in N8N:

### **Replace Nodes 10-11 with**: HTTP Request to Video Generation Service

**Deploy this to Vercel** (free tier):

```python
# filepath: vercel_api/text_video.py
from moviepy.editor import ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from flask import Flask, request, send_file

app = Flask(__name__)

@app.route('/generate-text-video', methods=['POST'])
def generate():
    data = request.json
    theme = data['theme']
    narration = data['narration']
    
    # Create 4 caption frames
    captions = [theme] + narration.split('. ')[:3]
    
    frames = []
    for caption in captions:
        img = Image.new("RGB", (1080, 1920), (10, 10, 14))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 56)
        
        # Center text (simplified)
        bbox = draw.textbbox((0, 0), caption, font=font)
        x = (1080 - (bbox[2] - bbox[0])) // 2
        y = (1920 - (bbox[3] - bbox[1])) // 2
        draw.text((x, y), caption, font=font, fill=(240, 240, 240))
        
        frames.append(img)
    
    # Create video
    clips = [ImageClip(np.array(f), duration=2.0) for f in frames]
    final = concatenate_videoclips(clips)
    final.write_videofile("video.mp4", fps=24)
    
    return send_file("video.mp4", mimetype="video/mp4")
```

Then in N8N:
- **Node 10**: HTTP Request to `https://your-vercel-app.vercel.app/generate-text-video`
- **Node 11**: Receives video binary directly

---

## 💰 COST BREAKDOWN

| Service | Monthly Cost |
|---------|--------------|
| **N8N Cloud** | $24 (Starter plan) |
| **YouTube API** | Free |
| **Groq API** | Free (30 req/min) |
| **Gemini Veo 3** | $3-9 (~$0.10-0.30/video) |
| **Vercel/Cloud Functions** | Free tier |
| **Google Sheets** | Free |
| **Total** | **$27-33/month** |

---

## ✅ ADVANTAGES OF N8N CLOUD ONLY

- ✅ **No local computer** needed
- ✅ **99.9% uptime** (cloud infrastructure)
- ✅ **Access from anywhere** (phone, tablet, laptop)
- ✅ **Built-in monitoring** (N8N Cloud dashboard)
- ✅ **Automatic scaling**
- ✅ **No maintenance** (N8N handles updates)
- ✅ **Visual workflow** (easier to debug than scripts)

---

## 🎯 NEXT STEPS

1. **Set up API keys** (30 min)
2. **Configure N8N credentials** (15 min)
3. **Build workflow nodes 1-13** (90 min)
4. **Deploy Veo 3 handler** to Cloud Functions (45 min)
5. **Test end-to-end** (30 min)
6. **Enable schedule trigger**
7. **Monitor first week**

---

## 📞 SUPPORT

- **N8N Docs**: https://docs.n8n.io/
- **N8N Community**: https://community.n8n.io/
- **YouTube API**: https://developers.google.com/youtube/v3
- **Veo 3 Access**: https://labs.google.com/veo

---

**Last Updated**: 2025-01-29  
**Version**: 1.0 (N8N Cloud Only Edition)
