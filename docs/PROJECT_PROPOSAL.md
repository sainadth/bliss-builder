# Project Name – Bliss Builder

## Primary Objective
Leverage an agentic framework to automate the end-to-end workflow of discovering trending ASMR themes, extracting themes using LLMs, generating detailed video narrations, creating 8-second YouTube Shorts using Google's Veo 3, and publishing them daily—without manual intervention.

## Core Architecture

### Modular Components

| Component | Technologies & Tools | Purpose |
|-----------|---------------------|---------|
| **ASMR Trend Fetching** | YouTube Data API v3 (Free) | Search trending ASMR videos using Search API with viewCount ordering, filter by ASMR keywords, fetch from last 7 days |
| **Theme Extraction** | Groq API with Llama 3.1-70b (Free tier) | Analyze all trending videos and extract ONE concise, brand-safe ASMR theme (6-14 words) |
| **Narration Generation** | Groq API with Llama 3.1-70b (Free tier) | Generate detailed 2-3 sentence video narration with sensory details suitable for Veo 3 prompt |
| **Video Generation** | Google Veo 3.1 API (google-genai SDK) | Generate 8-second ASMR video (1080x1920 portrait) using narration as prompt with proper polling mechanism |
| **Workflow Automation** | N8N Cloud (~$24/month) or Self-hosted (Free) | Orchestrate daily pipeline with timestamped output folders |
| **Storage** | Local filesystem with timestamped folders | Store trends.json, theme.txt, narration.txt, and video.mp4 per run |
| **Publishing** | YouTube Data API v3 (google-api-python-client, Free) | Automate daily uploads of YouTube Shorts with optimized metadata |

---

## Detailed Workflow

### Phase 1: ASMR Trend Discovery & Theme Extraction

**Step 1.1: Fetch ASMR-Specific Trending Videos**

**Primary Method: YouTube Search API**
```python
# trend_fetch.py implementation
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Search for ASMR videos sorted by viewCount (trending indicator)
request = youtube.search().list(
    part='snippet',
    q='ASMR',                      # Search query
    type='video',                  # Videos only
    order='viewCount',             # Most viewed (trending)
    maxResults=50,                 # Top 50
    relevanceLanguage='en',        # English content
    safeSearch='strict',           # Family-friendly
    videoDefinition='high',        # HD quality
    publishedAfter=(datetime.now() - timedelta(days=7)).isoformat() + 'Z'  # Last 7 days
)
response = request.execute()

# Extract video IDs from search results
video_ids = [item['id']['videoId'] for item in response['items']]

# Get full details including tags and view counts
videos_request = youtube.videos().list(
    part='snippet,statistics',
    id=','.join(video_ids)
)
videos_response = videos_request.execute()
```

**Fallback Method: Most Popular Chart with ASMR Filter**
```python
# If search fails, use mostPopular chart and filter
request = youtube.videos().list(
    part='snippet,statistics',
    chart='mostPopular',
    regionCode='US',
    maxResults=200  # Fetch more to filter
)
response = request.execute()

# Filter for ASMR-related content
asmr_keywords = ['asmr', 'relaxing', 'sleep', 'calm', 'whisper', 'tingles']
filtered_videos = [
    v for v in response['items']
    if any(kw in v['snippet']['title'].lower() for kw in asmr_keywords)
][:50]
```

**Output Structure**: `output/{timestamp}/trends.json`
```json
[
  {
    "video_id": "abc123",
    "title": "ASMR Rain Sounds for Deep Sleep - 10 Hours",
    "channel": "Peaceful ASMR",
    "description": "Gentle rain sounds with thunder...",
    "published_at": "2025-01-25T10:00:00Z",
    "hashtags": ["ASMR", "Rain", "Sleep", "Relaxing"],
    "keywords": ["rain sounds", "sleep", "asmr", "relaxing", "thunder"],
    "view_count": "1500000",
    "like_count": "45000"
  },
  // ...49 more videos
]
```

**ASMR Keyword Filter**:
```python
ASMR_KEYWORDS = [
    'asmr', 'relaxing', 'sleep', 'calm', 'soothing', 'meditation',
    'whisper', 'tingles', 'peaceful', 'ambient', 'calming', 'quiet',
    'soft spoken', 'rain sounds', 'nature sounds', 'white noise',
    'tapping', 'scratching', 'gentle', 'peaceful', 'stress relief'
]

def is_asmr_related(video):
    combined = f"{video['title']} {video['description']} {' '.join(video['keywords'])}"
    return any(kw in combined.lower() for kw in ASMR_KEYWORDS)
```

**Step 1.2: Extract Single ASMR Theme Using LLM**
```python
# Groq API analyzes top 15 trending videos
import requests

context = "\n\n".join([
    f"Title: {v['title']}\nKeywords: {', '.join(v['keywords'][:5])}\nHashtags: {', '.join(v['hashtags'][:5])}"
    for v in trends[:15]
])

prompt = f"""You are an ASMR content strategist. Based on these trending ASMR videos,
extract ONE concise theme (6-14 words) that captures current trends.
Be brand-safe, peaceful, imagery-focused. Abstract away brands/creators.

{context}

Output ONLY the theme line."""

response = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
    json={
        "model": "llama-3.1-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are an ASMR content expert."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 100,
        "temperature": 0.4
    }
)

theme = response.json()['choices'][0]['message']['content'].strip()
# Output: "gentle rain sounds over a peaceful forest path"
```
**Output**: `output/{timestamp}/theme.txt`

### Phase 2: Narration Generation

**Step 2.1: Generate Detailed Video Narration**
```python
# Extract context keywords from trends
context_keywords = []
for video in trends[:10]:
    context_keywords.extend(video['keywords'][:3])
    context_keywords.extend(video['hashtags'][:2])

unique_keywords = list(dict.fromkeys(context_keywords))[:10]

prompt = f"""You are an ASMR video director. Create a detailed 2-3 sentence narration
for an 8-second ASMR video based on this theme: '{theme}'

Context keywords from trending videos: {', '.join(unique_keywords)}

The narration should:
- Describe calming visuals (soft colors, gentle movements, peaceful scenes)
- Include sensory details (textures, sounds, ambiance)
- Be suitable for portrait format (1080x1920) YouTube Shorts
- Be brand-safe, peaceful, and meditative
- No text overlay, no people unless abstract/distant

Output ONLY the narration, ready to use as a video generation prompt."""

response = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
    json={
        "model": "llama-3.1-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a creative ASMR video director."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 250,
        "temperature": 0.7
    }
)

narration = response.json()['choices'][0]['message']['content'].strip()
# Output: "A peaceful 8-second journey through a misty forest path as gentle
# raindrops create soothing patterns on emerald leaves. Soft ambient sounds 
# blend with the rhythmic patter of rain. Serene greens and earth tones flow 
# in slow, meditative movements."
```
**Output**: `output/{timestamp}/narration.txt`

### Phase 3: Video Generation with Veo 3

**Step 3.1: Generate Video Using Veo 3.1 API (Updated)**
```python
from google import genai
from google.genai import types
import time

# Initialize client
client = genai.Client(api_key=GEMINI_API_KEY)

# Enhanced prompt
veo_prompt = f"""{narration}

CREATIVE REQUIREMENTS:
- VERTICAL 9:16 PORTRAIT FORMAT (1080x1920) REQUIRED for YouTube Shorts
- Camera MUST complete full cycle and return to EXACT starting position
- Use CIRCULAR or OSCILLATING motion (orbit, zoom cycle, rotation)
- NO LINEAR MOTION, NO CUTS
- Seamless loop - last frame matches first frame
- Smooth, meditative pacing
- Crystal clear, sharp details
- Generate synchronized ASMR audio"""

# Negative prompt to avoid unwanted content
negative_prompt = (
    "text overlays, watermarks, logos, people, faces, hands, "
    "urban scenes, cars, buildings, technology, screens, "
    "violent content, disturbing imagery, low quality, blurry, "
    "jerky motion, abrupt cuts, linear camera movement"
)

# Generate video with proper config
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=veo_prompt,
    config=types.GenerateVideosConfig(
        aspect_ratio="9:16",         # Portrait mode
        resolution="1080p",           # HD quality (options: 720p, 1080p)
        negative_prompt=negative_prompt,  # Avoid unwanted content
    ),
)

print(f"Operation started: {operation.name}")

# Poll for completion (typical: 2-5 minutes)
while not operation.done:
    time.sleep(10)
    operation = client.operations.get(operation)
    print("Polling...")

print("Video generation complete!")

# Download generated video
generated_video = operation.response.generated_videos[0]
client.files.download(file=generated_video.video)
generated_video.video.save("output/YYYYMMDD_HHMMSS/asmr_video.mp4")

print("Video saved successfully!")
```

**Output**: `output/{timestamp}/asmr_video.mp4` 
- Duration: 8 seconds
- Resolution: 1080x1920 portrait
- Format: MP4 (H.264)
- Size: ~5-15 MB
- Quality: Cinematic, HD

**Fallback (if Veo 3 unavailable)**:
```python
# Generate text-based video using MoviePy
from moviepy import ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Create 4 frames with theme + narration sentences
captions = [theme] + narration.split('. ')[:3]

frames = []
for caption in captions:
    img = Image.new("RGB", (1080, 1920), color=(10, 10, 14))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 56)
    
    # Word-wrap and center text
    # ...text rendering logic...
    
    frames.append(img)

# Create video clips (2 seconds per frame)
clips = [ImageClip(np.array(frame), duration=2.0) for frame in frames]
final = concatenate_videoclips(clips)
final.write_videofile("asmr_video.mp4", fps=24, codec="libx264")
```

### Phase 4: Publishing (YouTube Shorts Compliance)

**Step 4.1: Upload with AI Content Disclosure (Public Visibility)**

**Why Public is Safe**:
- ✅ **AI disclosure in description** (first 3 lines)
- ✅ **"AI-Generated" tags** clearly label content
- ✅ **Abstract ASMR visuals** (no people, no real events)
- ✅ **Peaceful, brand-safe content** (meditation/relaxation)
- ✅ **Compliant with YouTube TOS** (transparent about AI)
- ✅ **No copyright issues** (original AI-generated content)

**Compliant PUBLIC Upload Metadata**:
```python
body = {
    "snippet": {
        "title": f"ASMR Loop: {theme} #Shorts",
        "description": (
            f"#Shorts - {theme}\n\n"
            f"AI-GENERATED CONTENT: Created using Google Veo 3\n"
            f"SEAMLESS 8-SECOND LOOP - Perfect for endless relaxation\n\n"
            f"TRANSPARENCY NOTICE:\n"
            f"- Video: Generated by Google Veo 3 AI\n"
            f"- No real people, places, or events depicted\n"
            f"- Created for relaxation and meditation purposes\n\n"
            f"#AIGenerated #AIArt #SyntheticMedia #ASMR\n\n"
            f"Best with headphones | Subscribe for daily AI-generated ASMR Shorts\n\n"
            f"DISCLAIMER: AI-generated content for entertainment and relaxation.\n"
            f"No copyright infringement intended. All visuals are original AI creations."
        ),
        "tags": [
            "Shorts", "ASMR", "AI Generated", "AI Art", 
            "Synthetic Media", "AI ASMR", "Google Veo"
        ],
        "categoryId": "22"
    },
    "status": {
        "privacyStatus": "public",  # SAFE: Public with AI disclosure
        "selfDeclaredMadeForKids": False,
        "madeForKids": False
    }
}
```

**Public Visibility Benefits**:
1. ✅ **Reach wider audience** (Shorts feed, search, recommendations)
2. ✅ **Monetization eligible** (if channel meets requirements)
3. ✅ **Algorithmic promotion** (YouTube pushes Shorts to viewers)
4. ✅ **Engagement growth** (likes, comments, shares)
5. ✅ **Brand building** (channel growth, subscribers)

**Safety Checklist for Public Content**:
- ✅ **AI disclosure in title/description** (prevents misleading)
- ✅ **No fake personas** (our ASMR is abstract nature scenes)
- ✅ **No copyrighted content** (all AI-generated originals)
- ✅ **Family-friendly** (peaceful ASMR only)
- ✅ **Educational/entertainment purpose** (relaxation, meditation)
- ✅ **No controversial topics** (brand-safe, calming content)

### Phase 5: N8N Automation

**Daily Workflow (Cron: 0 15 * * *)**:
```
1. Schedule Trigger (3 PM)
   ↓
2. Execute trend_fetch.py
   --output-json output/{timestamp}/trends.json
   --output-theme output/{timestamp}/theme.txt
   --region US
   --max 50
   ↓
3. Execute gemini_video.py
   --trends-json output/{timestamp}/trends.json
   --theme-file output/{timestamp}/theme.txt
   --output output/{timestamp}/asmr_video.mp4
   --output-narration output/{timestamp}/narration.txt
   --duration 8
   ↓
4. Execute youtube_upload.py
   --video output/{timestamp}/asmr_video.mp4
   --theme-file output/{timestamp}/theme.txt
   ↓
5. Write log entry to output/pipeline_log.csv
```

**Output Structure**:
```
output/
├── 20250129_150000/
│   ├── trends.json          # 50 ASMR trending videos (JSON)
│   ├── theme.txt             # Extracted theme (single line)
│   ├── narration.txt         # Generated narration (2-3 sentences)
│   └── asmr_video.mp4        # Final video (8s, 1080x1920, ~5-15MB)
├── 20250130_150000/
│   └── ...
└── pipeline_log.csv          # Execution log
```

**Log Format** (`pipeline_log.csv`):
```csv
timestamp,success,theme,video_id,video_url,error
20250129_150000,true,"gentle rain over peaceful forest","dQw4w9WgXcQ","https://youtube.com/shorts/dQw4w9WgXcQ",None
20250130_150000,false,"N/A","","","Video generation timeout"
```

---

## Timeline (8 Weeks)

| Weeks | Milestones |
|-------|-----------|
| **Weeks 1-2** | ✅ Setup YouTube Data API, Gemini API, Groq API. Implement trend fetching with Search API and ASMR filtering. |
| **Weeks 3-4** | ✅ Integrate Groq for theme extraction and narration generation. Test with sample data. |
| **Week 5** | ✅ Implement Veo 3.1 video generation with proper polling. Generate sample 8-second ASMR Shorts. |
| **Week 6** | Build YouTube upload script with OAuth2. Test manual uploads with metadata. |
| **Week 7** | Integrate all modules into N8N workflows. Implement daily scheduling with timestamped folders. |
| **Week 8** | End-to-end testing, pilot daily uploads, analytics gathering, documentation. |

---

## Key Deliverables

1. **Fully Automated Agentic Pipeline**  
   - Zero manual intervention after initial setup
   - Runs daily at 3 PM via N8N cron trigger

2. **Daily YouTube Shorts**  
   - 8-second high-quality ASMR videos generated by Veo 3.1
   - Optimized for vertical (1080x1920) format
   - Trending ASMR themes based on real-time YouTube data

3. **Cost-Effective Solution**  
   - YouTube Data API: **Free** (10k quota/day, uses ~100 units/day)
   - Groq (LLM): **Free tier** (30 req/min, uses 2 req/day)
   - Gemini Veo 3: **~$3-9/month** (pay-per-use, ~$0.10-0.30/video)
   - N8N: **Self-hosted (free)** or **Cloud ($24/month)**
   - **Total estimated cost: $3-33/month**

4. **Soothing, Trending Content**  
   - Videos aligned with current ASMR trends from YouTube
   - Brand-safe, family-friendly content
   - Optimized for engagement (hashtags, metadata, timing)

---

## Technical Stack Summary

- **Languages**: Python 3.11+
- **Key Libraries**:  
  - `google-api-python-client` (YouTube Data API v3)
  - `google-genai` (Veo 3.1 video generation with polling)
  - `requests` (Groq API HTTP calls)
  - `moviepy`, `Pillow` (fallback video/image processing)
  - `python-dotenv` (environment management)
- **APIs Used**:
  - YouTube Data API v3: `search().list()`, `videos().list()`, `videos().insert()`
  - Groq API: `llama-3.1-70b-versatile` model
  - Gemini Veo 3.1 API: `veo-3.1-generate-preview` model
- **Orchestration**: N8N (workflow automation with cron triggers)
- **Storage**: Local filesystem with timestamped folders (`output/YYYYMMDD_HHMMSS/`)
- **Version Control**: Git + GitHub

---

## API Usage & Rate Limits

### YouTube Data API v3
- **Quota**: 10,000 units/day (free)
- **Daily Usage**:
  - `search().list()`: 100 units (1x/day)
  - `videos().list()`: 1-3 units (2x/day)
  - `videos().insert()`: 1,600 units (1x/day)
  - **Total**: ~1,700 units/day (17% of quota)

### Groq API
- **Quota**: 30 requests/minute (free tier)
- **Daily Usage**: 2 requests/day (theme + narration)
- **Cost**: $0

### Gemini Veo 3.1 API
- **Quota**: Pay-per-use
- **Daily Usage**: 1 video/day (8 seconds)
- **Cost**: ~$0.10-0.30/video = **$3-9/month**

---

## Success Metrics

- **Consistency**: Daily uploads at 3 PM without failures
- **Engagement**: 
  - Target: >100 views per video within 24 hours
  - Target: >4 seconds average watch time (50% completion)
  - Target: >5% like rate
- **Cost Efficiency**: Stay within $33/month budget
- **Quality**: 
  - Videos align with trending ASMR themes
  - Positive feedback in comments
  - No copyright/community guideline issues

---

## Extensions (Future Enhancements)

1. **Real-Time Trend Adaptation**  
   - Monitor Reddit r/asmr, Twitter trends, TikTok sounds
   - Adjust theme extraction based on emerging patterns

2. **Personalized ASMR Content**  
   - Analyze your channel's top-performing videos
   - Tailor themes based on subscriber preferences

3. **Content Uniqueness**  
   - Layer custom ASMR sounds (rain, tapping, whispers) using FFmpeg
   - Generate unique audio tracks with AI

4. **Multi-Platform Publishing**  
   - Auto-post to TikTok, Instagram Reels, Pinterest
   - Cross-platform hashtag optimization

5. **A/B Testing**  
   - Generate 2-3 video variants per theme
   - Publish at different times, measure engagement
   - Use winning variant formula for future videos

---

## Security & Best Practices

### API Key Management
```bash
# .env file (never commit to GitHub)
YOUTUBE_API_KEY=AIzaSy...
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=AIzaSy...
```

### .gitignore
```
.env
youtube_credentials.json
output/
*.mp4
*.json
__pycache__/
```

### Error Handling
- All scripts include try/catch with fallbacks
- Retry logic for transient API failures
- Detailed error logging in `pipeline_log.csv`

### AI Content Compliance

**Mandatory Disclosures**:
```python
# Always include in video descriptions
AI_DISCLOSURE = """
🤖 AI-GENERATED CONTENT
This video was created using AI technology (Google Veo 3).
No real people, places, or events are depicted.
Created for relaxation and entertainment purposes only.
"""
```

**Recommended Practices**:
1. **Description**: Always mention "AI-generated" in first 3 lines
2. **Tags**: Include "AI Generated", "Synthetic Media", "AI Art"
3. **Thumbnails**: If used, label with "AI-generated" text overlay
4. **Comments**: Pin comment explaining AI creation process
5. **Channel About**: State that content is AI-generated

**YouTube Studio Settings**:
- Enable "Altered content" disclosure (if feature available)
- Select "Synthetic or altered media" category
- Check "Content features realistic people or events" = NO

### Content Safety

**To Avoid Strikes/Flags**:
- Use abstract/non-realistic AI visuals (our ASMR content ✓)
- Avoid generating faces, identifiable people
- No political, religious, or controversial content
- No copyrighted music, logos, or trademarks
- Family-friendly content only (our ASMR ✓)
- Clear meditation/relaxation purpose (our ASMR ✓)

**Why Our Content is Low-Risk**:
- ✅ Abstract nature scenes (not photorealistic people)
- ✅ Original AI-generated visuals (no copyright)
- ✅ Peaceful ASMR theme (brand-safe)
- ✅ Educational/wellness purpose
- ✅ Transparent AI disclosure
- ✅ No misleading claims

---

## Conclusion

Bliss Builder v3 is a production-ready, cost-effective system that leverages:
- **Real YouTube Data API** for authentic ASMR trend discovery
- **Groq LLM (free)** for intelligent theme extraction and narration
- **Google Veo 3.1** for high-quality 8-second video generation
- **N8N** for reliable daily automation

The system is scalable, maintainable, and optimized for zero manual intervention after initial setup.

---

**Last Updated**: 2025-01-29  
**Version**: 3.0 (Production Release)  
**Status**: ✅ Phase 1-3 Complete, Phase 4-5 In Progress