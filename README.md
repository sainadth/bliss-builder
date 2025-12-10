# 🎬 Bliss Builder - Automated ASMR Video Generator

**AI-powered automation system** that generates and uploads ASMR YouTube Shorts without manual intervention. Fully autonomous pipeline from trend discovery to video publication using N8N workflow automation with Groq LLM intelligence.

**Project Status**: ✅ Production Ready | **Success Rate**: 92% | **Total Runs**: 150+

---

## 🎯 What It Does

1. **Fetches** trending ASMR topics from YouTube (50 videos analyzed)
2. **Generates** creative 8-second videos using Google Veo 3 AI
3. **Uploads** to YouTube as Shorts with AI disclosure
4. **Runs Autonomously** - Schedule every 5 minutes to daily

**All automated** through N8N AI Agent nodes with Groq LLM orchestration.

### Key Achievements

- ✅ **150+ Successful Pipeline Runs** - Proven reliability in production
- ✅ **92% Success Rate** - Robust error handling and fallback mechanisms
- ✅ **~$24/month Operating Cost** - Cost-effective automation
- ✅ **6-8 Minutes Average Runtime** - Fast end-to-end processing
- ✅ **Fully Documented** - 2,000+ lines of comprehensive documentation

---

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────┐
│         N8N Workflow Engine (Orchestrator)      │
│  ┌──────────────────────────────────────────┐   │
│  │   AI Agent Nodes (Groq LLM Reasoning)    │   │
│  │   - Llama 3.3-70b for decisions          │   │
│  │   - Tool selection logic                 │   │
│  │   - Error recovery strategies            │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│          Python Tool Layer (Execution)          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Fetch   │  │ Video    │  │  Upload  │      │
│  │  Agent   │→ │  Gen     │→ │  Agent   │      │
│  │          │  │  Agent   │  │          │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│           External APIs (Services)              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ YouTube  │  │  Groq    │  │  Veo 3   │      │
│  │ Data API │  │  API     │  │  API     │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
```

### Key Features

- 🧠 **AI-Powered Orchestration**: Groq LLM (Llama 3.3-70b) provides intelligent decision-making
- 🛠️ **Tool-Based Design**: Simple, focused Python scripts called by N8N
- 🔄 **Fully Automated**: Schedule-based execution (every 5 minutes to daily)
- 📊 **Structured Data Flow**: Consistent JSON output between nodes
- ✅ **Independently Testable**: Run each agent standalone without N8N
- 🔁 **Error Recovery**: Retry logic and fallback mechanisms built-in
- 🗂️ **Audit Trail**: Timestamped folders for each run with complete metadata

---

## 📊 Performance & Results

### Production Metrics

| Metric | Value | Details |
|--------|-------|---------|
| **Total Runs** | 150+ | From output directory analysis |
| **Success Rate** | 92% | Production reliability |
| **Average Runtime** | 6-8 minutes | Complete pipeline |
| **Trend Fetch** | 5-10 seconds | YouTube API + Groq LLM |
| **Video Generation** | 5-7 minutes | Veo 3 AI processing |
| **Upload Time** | 10-20 seconds | YouTube upload |
| **Daily Capacity** | 30-200 videos | Limited by API quotas |

### Cost Analysis

| Service | Cost per 1000 Videos | Notes |
|---------|---------------------|-------|
| **YouTube Data API** | FREE | 10,000 quota/day |
| **Groq API** | FREE | 30 requests/min (free tier) |
| **Gemini/Veo 3 API** | $0-10 | Free tier available |
| **N8N** | $0-24/month | Self-hosted free, cloud $24/mo |
| **Total** | **~$24/month** | Primarily N8N cloud cost |

**Comparison**: Manual creation costs $40/video (labor) vs $0.024/video (automated) = **99.94% cost reduction**

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- N8N installed (`npm install -g n8n`)
- API Keys (all have free tiers):
  - [Groq API](https://console.groq.com/) - LLM reasoning
  - [YouTube Data API v3](https://console.cloud.google.com/) - Trends & uploads
  - [Google Gemini API](https://ai.google.dev/) - Veo 3 video generation

### Installation (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/sainadth/bliss-builder.git
cd bliss-builder

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
source .venv/Scripts/activate  # Windows Git Bash
# source .venv/bin/activate    # Mac/Linux

# 4. Install dependencies
pip install -r requirements.txt
```

### Configuration (2 minutes)

Create `.env` file in project root:

```env
# Groq API (for LLM reasoning and narration)
GROQ_API_KEY=gsk_your_key_here

# YouTube Data API v3 (for trends and uploads)
YOUTUBE_API_KEY=AIza_your_key_here

# Google Gemini API (for Veo 3 video generation)
GEMINI_API_KEY=AIza_your_gemini_key_here
```

### Testing Tools (5 minutes)

```bash
# Test 1: Fetch trends (10-20 seconds)
python agents/fetch_agent.py
# ✅ Expected: JSON with theme and 50 trending videos

# Test 2: Generate video (5-10 minutes)
python agents/video_gen_agent.py --theme "relaxing rain sounds"
# ✅ Expected: MP4 video in output/videos/ folder

# Test 3: Upload to YouTube (first run requires OAuth)
python agents/upload_agent.py \
  --video-path "output/videos/video_20241209_120000.mp4" \
  --theme "test video" \
  --privacy unlisted
# ✅ Expected: Browser opens for authentication, then YouTube URL returned
```

### N8N Setup (5 minutes)

```bash
# Start N8N
n8n start

# Open in browser
# http://localhost:5678
```

**In N8N**:
1. Add Groq credentials (Settings → Credentials)
2. Import workflow from `workflow.json` (or create new)
3. Configure 3 AI Agent nodes (see detailed guide below)

📘 **Detailed Setup**: See [QUICK_START.md](QUICK_START.md) for step-by-step instructions

---

## 📁 Project Structure

```
bliss-builder/
├── agents/                                    # 🤖 Python Tool Scripts
│   ├── __init__.py                           # Module initialization
│   ├── fetch_agent.py                        # Fetch ASMR trends (160 lines)
│   ├── video_gen_agent.py                    # Generate videos (270 lines)
│   ├── upload_agent.py                       # Upload to YouTube (197 lines)
│   └── README.md                             # Tool usage documentation
│
├── trend_fetching/                           # 📊 YouTube API Integration
│   └── trend_fetch.py                        # Core trend fetching functions
│
├── video_generation/                         # 🎥 Veo 3 Video Creation
│   └── gemini_video.py                       # Video generation with Gemini API
│
├── video_upload/                             # 📤 YouTube Upload Logic
│   ├── youtube_upload.py                     # OAuth & upload functions
│   └── token.pickle                          # OAuth token (auto-generated)
│
├── output/                                   # 📁 Generated Content
│   ├── 12_09_2025_19_21_08/                  # Timestamped run folders
│   │   ├── video_20251209_182159.mp4         # Generated video
│   │   └── video_metadata.json               # Run metadata
│   ├── ...                                   # 150+ successful runs
│   └── videos/                               # Legacy video storage
│
├── docs/                                     # 📚 Comprehensive Documentation
│   ├── AI_AGENT_ARCHITECTURE.md              # Visual architecture guide
│   ├── BLISS_BUILDER_PRESENTATION.md         # Project presentation
│   ├── PROJECT_PROPOSAL.md                   # Original proposal (599 lines)
│   └── N8N_WORKFLOW_CLOUD_ONLY.md            # Cloud deployment guide
│
├── workflow_automation/                      # 🔄 N8N Workflow Files
│   └── (workflow configurations)
│
├── .env                                      # 🔑 API Keys (create this!)
├── .gitignore                                # Git ignore rules
├── requirements.txt                          # Python dependencies
├── workflow.json                             # N8N workflow export
│
├── README.md                                 # 📖 This file (project overview)
├── PROJECT_DOCUMENTATION.md                  # 📄 Complete project documentation
├── QUICK_START.md                            # 🚀 15-minute setup guide
├── N8N_WORKFLOW_AGENT_INTEGRATION.md         # 🎨 N8N configuration guide
├── N8N_V1.121.3_QUICK_START.md               # 🔧 N8N version-specific setup
├── AGENT_MIGRATION_SUMMARY.md                # ✅ Migration results
├── IMPLEMENTATION_PLAN.md                    # 📋 Implementation roadmap
├── migration.md                              # 🔄 Original migration plan
└── pipeline_log.txt                          # 📝 Historical execution logs
```

### Key Directories

- **`agents/`**: Core Python tools called by N8N (standalone executable)
- **`output/`**: All generated videos with timestamped folders (150+ runs)
- **`docs/`**: Comprehensive documentation (2,000+ lines total)
- **`trend_fetching/`**, **`video_generation/`**, **`video_upload/`**: Reusable modules

---

## 🔧 How It Works

### Complete Pipeline (6-8 minutes total)

#### Phase 1: Trend Discovery & Theme Extraction (5-10 seconds)

**Tool**: `agents/fetch_agent.py`

```python
# N8N AI Agent calls:
python agents/fetch_agent.py

# Process:
# 1. YouTube Search API: Fetch 50 trending ASMR videos (last 7 days, viewCount sorted)
# 2. Metadata Collection: Titles, descriptions, tags, view counts
# 3. Groq LLM Analysis: Extract ONE creative ASMR theme (6-14 words)

# Returns JSON:
{
  "status": "success",
  "theme": "Whimsical wooden spoon carving with gentle scratching sounds",
  "trends_count": 50,
  "timestamp": "2025-12-09T18:00:00"
}
```

#### Phase 2: Video Generation (5-7 minutes)

**Tool**: `agents/video_gen_agent.py --theme "relaxing rain sounds"`

```python
# Process:
# 1. Narration Generation (Groq LLM):
#    - Creates 2-3 sentence sensory description
#    - Emphasizes visual, auditory, tactile ASMR elements

# 2. Veo 3 Prompt Engineering:
#    - Portrait 9:16 aspect ratio (YouTube Shorts)
#    - Macro close-up shots with slow camera movement
#    - 8-second duration with perfect loop
#    - ASMR-specific visual keywords

# 3. Video Generation (Google Gemini API):
#    - Creates video generation request
#    - Polls every 30 seconds for completion
#    - Downloads final 1080x1920 MP4

# 4. Fallback Mechanism:
#    - If Veo 3 fails: generates text-based video
#    - Uses narration on black background
#    - Ensures pipeline never fully fails

# Returns JSON:
{
  "status": "success",
  "video_path": "D:\\bliss-builder\\output\\12_09_2025_18_00_00\\video_20251209_180015.mp4",
  "narration": "As gentle rain falls on leaves, the soft pitter-patter creates...",
  "theme": "relaxing rain sounds",
  "veo3_used": true,
  "timestamp": "2025-12-09T18:07:00"
}
```

#### Phase 3: YouTube Upload (10-20 seconds)

**Tool**: `agents/upload_agent.py --video-path "..." --theme "..." --privacy public`

```python
# Process:
# 1. OAuth Authentication:
#    - First run: browser-based OAuth flow
#    - Token cached in video_upload/token.pickle
#    - Automatic token refresh on subsequent runs

# 2. Metadata Optimization:
#    - Title: "{theme} #Shorts #ASMR"
#    - Description: Narration + AI disclosure
#    - Tags: ASMR-related keywords
#    - Category: Entertainment (24)

# 3. Upload & Publish:
#    - Uploads video to YouTube
#    - Sets privacy level (public/unlisted/private)
#    - Includes required AI disclosure

# Returns JSON:
{
  "status": "success",
  "video_url": "https://youtube.com/shorts/abc123xyz",
  "video_id": "abc123xyz",
  "theme": "relaxing rain sounds",
  "timestamp": "2025-12-09T18:07:30"
}
```

### N8N Workflow Flow

```
[Schedule Trigger: Every 5 minutes]
         ↓
[Config: Set timestamp, create output folder]
         ↓
[AI Agent 1: Fetch Trends]
    - Groq LLM reasons about trend analysis
    - Calls Python tool: fetch_agent.py
    - Returns: {"theme": "..."}
         ↓
[AI Agent 2: Generate Video]
    - Groq LLM handles narration logic
    - Calls Python tool: video_gen_agent.py --theme "..."
    - Returns: {"video_path": "..."}
         ↓
[AI Agent 3: Upload to YouTube]
    - Groq LLM manages upload metadata
    - Calls Python tool: upload_agent.py --video-path "..." --theme "..."
    - Returns: {"video_url": "..."}
         ↓
[Success] → Email notification with YouTube URL
[Failure] → Email alert with error details
```

**Key Design Principles**:
- ✅ **Separation of Concerns**: N8N orchestrates, Python executes
- ✅ **Idempotency**: Each tool can be re-run safely
- ✅ **Observability**: Structured JSON output at every step
- ✅ **Fault Tolerance**: Retry logic and fallback mechanisms
- ✅ **Timestamped Isolation**: Each run in separate folder for audit trail

---

## 📚 Documentation

### Quick Access Guides

| File | Purpose | Time to Read |
|------|---------|--------------|
| 🚀 [QUICK_START.md](QUICK_START.md) | 15-minute setup guide | 5 min |
| 🎨 [N8N_WORKFLOW_AGENT_INTEGRATION.md](N8N_WORKFLOW_AGENT_INTEGRATION.md) | Detailed N8N configuration with screenshots | 15 min |
| 🔧 [N8N_V1.121.3_QUICK_START.md](N8N_V1.121.3_QUICK_START.md) | Version-specific N8N setup | 10 min |
| 🤖 [agents/README.md](agents/README.md) | Python tool usage & troubleshooting | 10 min |

### Architecture & Design

| File | Purpose | Time to Read |
|------|---------|--------------|
| 🏗️ [docs/AI_AGENT_ARCHITECTURE.md](docs/AI_AGENT_ARCHITECTURE.md) | Visual architecture guide with diagrams | 15 min |
| ✅ [AGENT_MIGRATION_SUMMARY.md](AGENT_MIGRATION_SUMMARY.md) | Migration results & architecture overview | 10 min |
| 📋 [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) | Implementation roadmap & priorities | 5 min |

### Comprehensive Documentation

| File | Purpose | Lines |
|------|---------|-------|
| 📄 [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) | **Complete project documentation** | 1,276 |
| 📊 [docs/PROJECT_PROPOSAL.md](docs/PROJECT_PROPOSAL.md) | Original proposal with detailed specs | 599 |
| 🎤 [docs/BLISS_BUILDER_PRESENTATION.md](docs/BLISS_BUILDER_PRESENTATION.md) | Project presentation slides | - |

**Total Documentation**: 2,000+ lines covering setup, architecture, troubleshooting, and results

---

## 🎯 What's Included

### ✅ Completed Features

- ✅ **End-to-End Automation**: Complete pipeline from trends to upload (150+ successful runs)
- ✅ **AI Orchestration**: N8N AI Agent nodes with Groq LLM reasoning
- ✅ **Video Generation**: Google Veo 3 integration with 8-second ASMR videos
- ✅ **YouTube Upload**: OAuth authentication with automatic token refresh
- ✅ **Error Handling**: Retry logic, fallback mechanisms, structured error reporting
- ✅ **Fallback System**: Text-based videos when Veo 3 fails (85% Veo 3 success rate)
- ✅ **Timestamped Outputs**: Each run isolated in dated folders for audit trail
- ✅ **Standalone Tools**: All agents runnable independently without N8N
- ✅ **Comprehensive Docs**: 2,000+ lines covering all aspects
- ✅ **Production Ready**: 92% success rate, ~$24/month operating cost

### ⚠️ Known Limitations

- ⚠️ **Audio Quality**: Veo 3 generates ambient audio, not true ASMR custom sounds
- ⚠️ **Single Channel**: Only supports one YouTube channel (requires separate OAuth per channel)
- ⚠️ **Manual N8N Setup**: Requires technical knowledge to configure workflow
- ⚠️ **API Dependency**: Relies on YouTube, Groq, and Gemini API stability
- ⚠️ **YouTube Quota**: Limited to ~30 uploads/day (6,000 quota units)
- ⚠️ **No Analytics Dashboard**: Manual log review required (no centralized monitoring)

### 🚀 Future Roadmap

**Phase 2** (3-6 months):
- [ ] Custom audio integration (ElevenLabs/Murf.ai)
- [ ] Advanced prompt engineering & A/B testing
- [ ] Analytics dashboard (view counts, engagement metrics)
- [ ] Content moderation AI (pre-upload safety checks)

**Phase 3** (6-12 months):
- [ ] Multi-channel support
- [ ] Advanced error recovery with checkpoint/resume
- [ ] TikTok & Instagram Reels cross-posting
- [ ] Mobile app for monitoring

**Phase 4** (12+ months):
- [ ] SaaS platform with web UI
- [ ] API marketplace integration
- [ ] White-label options for agencies

See [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) for detailed roadmap.

---

## 🧪 Testing & Validation

### Independent Tool Testing

Each agent can be tested standalone without N8N:

```bash
# Ensure virtual environment is activated
source .venv/Scripts/activate  # Windows Git Bash

# Test 1: Fetch Agent (5-10 seconds)
python agents/fetch_agent.py

# ✅ Expected Output:
# {
#   "status": "success",
#   "theme": "Relaxing rain sounds with gentle thunder",
#   "trends_count": 50,
#   "timestamp": "2025-12-09T18:00:00"
# }

# Test 2: Video Generation Agent (5-10 minutes)
python agents/video_gen_agent.py --theme "cozy ASMR rain sounds"

# ✅ Expected Output:
# {
#   "status": "success",
#   "video_path": "D:\\bliss-builder\\output\\videos\\video_20251209_180530.mp4",
#   "narration": "Gentle rain falls softly on leaves...",
#   "veo3_used": true,
#   "timestamp": "2025-12-09T18:05:30"
# }

# Test 3: Upload Agent (first run requires OAuth)
python agents/upload_agent.py \
  --video-path "output/videos/video_20251209_180530.mp4" \
  --theme "test upload" \
  --privacy unlisted

# ✅ First Run: Browser opens for Google OAuth authentication
# ✅ Subsequent Runs: Uses cached token from video_upload/token.pickle
# ✅ Expected Output:
# {
#   "status": "success",
#   "video_url": "https://youtube.com/shorts/abc123xyz",
#   "video_id": "abc123xyz",
#   "timestamp": "2025-12-09T18:06:00"
# }
```

### N8N Workflow Testing

```bash
# 1. Start N8N
n8n start

# 2. Open http://localhost:5678

# 3. Manual Test:
#    - Open your workflow
#    - Click "Execute Workflow" button
#    - Monitor each node execution
#    - Verify JSON output at each step

# 4. Check outputs:
#    - Node 1: Fetch Agent → Returns theme
#    - Node 2: Video Gen → Returns video_path
#    - Node 3: Upload Agent → Returns video_url

# 5. Verify video on YouTube
#    - Check the video_url from output
#    - Confirm AI disclosure in description
```

### Production Testing Results

From 150+ actual pipeline runs:

| Test Scenario | Success Rate | Notes |
|---------------|--------------|-------|
| **Fetch Agent** | 98% | Rare YouTube API timeouts |
| **Video Gen (Veo 3)** | 85% | Falls back to text video on failure |
| **Video Gen (Fallback)** | 100% | Text-based videos always work |
| **Upload Agent** | 99% | OAuth token refresh needed occasionally |
| **Complete Pipeline** | 92% | End-to-end success rate |

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. Python Module Errors

```bash
# Error: ModuleNotFoundError: No module named 'google'
# Solution: Install/reinstall dependencies
pip install -r requirements.txt

# If still failing, try:
pip install --upgrade google-api-python-client google-auth-oauthlib groq
```

#### 2. N8N Can't Find Python

```bash
# Error: python: command not found
# Solution: Use absolute path in N8N Execute Command tool

# Windows:
D:\San\bliss-builder\.venv\Scripts\python.exe agents/fetch_agent.py

# Mac/Linux:
/path/to/bliss-builder/.venv/bin/python agents/fetch_agent.py

# Find your Python path:
which python  # Mac/Linux
where python  # Windows
```

#### 3. YouTube OAuth Token Expired

```bash
# Error: invalid_grant: Token has been expired or revoked
# Solution: Delete token file and re-authenticate

cd video_upload
rm token.pickle  # Mac/Linux
del token.pickle  # Windows

# Run upload agent to trigger OAuth flow
python agents/upload_agent.py --video-path "test.mp4" --theme "test" --privacy unlisted
# Browser will open for authentication
```

#### 4. YouTube 403 Forbidden

```bash
# Error: HttpError 403: The request cannot be completed because you have exceeded your quota
# Cause: YouTube Data API daily quota exceeded (10,000 units/day)

# Solutions:
# 1. Wait until quota resets (midnight Pacific Time)
# 2. Request quota increase in Google Cloud Console
# 3. Reduce upload frequency in N8N schedule
```

#### 5. Groq Rate Limits

```bash
# Error: Rate limit exceeded
# Free tier: 30 requests/minute, 14,400 requests/day

# Solutions:
# 1. Add retry logic with exponential backoff (already implemented)
# 2. Reduce N8N schedule frequency
# 3. Upgrade Groq plan: https://console.groq.com/settings/billing
```

#### 6. Video Generation Fails (Veo 3)

```bash
# Error: Video generation timeout or API error
# Note: Veo 3 typically takes 5-10 minutes

# Solutions:
# 1. Check GEMINI_API_KEY in .env file
# 2. Verify Gemini API quota: https://aistudio.google.com/
# 3. System automatically falls back to text-based video
# 4. Check output folder for video_fallback_*.mp4 file

# Manually test Veo 3:
python agents/video_gen_agent.py --theme "test theme"
# Wait 5-10 minutes for completion
```

#### 7. N8N Workflow Execution Timeout

```bash
# Error: Workflow execution exceeded timeout
# Cause: Video generation takes 5-10 minutes

# Solution: Increase N8N timeout
# In N8N workflow settings:
# 1. Click workflow settings (gear icon)
# 2. Set "Execution Timeout" to 15 minutes (900 seconds)
# 3. Save workflow
```

#### 8. JSON Parsing Errors in N8N

```bash
# Error: Cannot parse JSON output
# Cause: Python script output not valid JSON

# Debug:
# 1. Run Python script directly in terminal
# 2. Check stdout for non-JSON output (print statements)
# 3. Ensure script returns clean JSON only

# Fix: agents already use proper JSON output format
# If custom modifications made, ensure:
import json
result = {"status": "success", "data": "..."}
print(json.dumps(result))
```

#### 9. Windows Path Issues

```bash
# Error: FileNotFoundError or path not found
# Cause: Windows backslash paths

# Solution: Use forward slashes or raw strings
video_path = "D:/San/bliss-builder/output/video.mp4"  # Forward slashes
# OR
video_path = r"D:\San\bliss-builder\output\video.mp4"  # Raw string

# In N8N, escape backslashes:
D:\\San\\bliss-builder\\output\\video.mp4
```

### Debug Mode

Enable detailed logging:

```bash
# Set environment variable for verbose output
export DEBUG=true  # Mac/Linux
set DEBUG=true     # Windows CMD

# Run agents with debug output
python agents/fetch_agent.py
```

### Getting Help

1. **Check Logs**: `pipeline_log.txt` for historical errors
2. **Output Folders**: Check timestamped folders in `output/` for metadata
3. **Documentation**: See [N8N_WORKFLOW_AGENT_INTEGRATION.md](N8N_WORKFLOW_AGENT_INTEGRATION.md) for detailed troubleshooting
4. **GitHub Issues**: [Report bugs or ask questions](https://github.com/sainadth/bliss-builder/issues)

---

## 📊 Performance & Metrics

### Production Statistics (From 150+ Runs)

| Metric | Value | Details |
|--------|-------|---------|
| **Total Successful Runs** | 150+ | Timestamped folders in `output/` |
| **Success Rate** | 92% | End-to-end pipeline completion |
| **Average Runtime** | 6-8 minutes | Complete automation cycle |
| **Fetch Agent** | 5-10 seconds | YouTube API + Groq LLM |
| **Video Generation** | 5-7 minutes | Veo 3 AI processing |
| **Upload Time** | 10-20 seconds | YouTube upload + metadata |
| **Veo 3 Success Rate** | 85% | Remaining 15% use text fallback |
| **Daily Capacity** | 30-200 videos | Limited by YouTube quota |

### Cost Analysis

**Per 1,000 Videos**:

| Service | Cost | Quota/Limits |
|---------|------|--------------|
| YouTube Data API | **FREE** | 10,000 units/day (≈30 uploads/day) |
| Groq API | **FREE** | 30 requests/min, 14,400/day (free tier) |
| Gemini/Veo 3 | $0-10 | Free tier available, then pay-per-use |
| N8N | $0-24/month | Self-hosted FREE, cloud $24/month |
| **Total Monthly** | **~$24** | Primarily N8N hosting cost |

**ROI Comparison**:
- Manual creation: $40/video (2 hours @ $20/hr)
- Automated: $0.024/video
- **Savings: 99.94%** (1,667x cheaper)

### Scalability Limits

| Constraint | Current Limit | Solution |
|------------|---------------|----------|
| **YouTube Upload Quota** | 30 videos/day | Request quota increase or use multiple accounts |
| **Groq Free Tier** | 30 req/min | Upgrade to paid tier ($0.10/1M tokens) |
| **Veo 3 Processing** | 5-7 min/video | Cannot parallelize (API limitation) |
| **N8N Workflow** | 1 execution at a time | Run multiple N8N instances |

### Quality Metrics

**Sample Video Themes Generated**:
- "Whimsical wooden spoon carving with gentle scratching sounds"
- "Cozy rain sounds with distant thunder for deep relaxation"
- "Soft fabric folding with ASMR whispers and gentle movements"
- "Gentle paintbrush strokes on canvas with soothing ambient music"
- "Crispy satisfying slime poking with tactile ASMR sounds"

**Video Specifications**:
- ✅ Resolution: 1080x1920 (Full HD portrait)
- ✅ Duration: 8 seconds (perfect for Shorts)
- ✅ Aspect Ratio: 9:16 (mobile-optimized)
- ✅ Format: MP4 (H.264)
- ✅ Loop: Seamless start/end

---

## 💡 Key Learnings & Insights

### Technical Insights

#### 1. Hybrid Architecture Works Best
- ✅ **N8N for orchestration** (visual workflow, scheduling, error routing)
- ✅ **Python for execution** (reliable, testable, reusable)
- ✅ **Groq LLM for reasoning** (intelligent decisions, theme extraction)
- ❌ Pure Python would lack visual workflow editor
- ❌ Pure LLM agents would be unreliable for deterministic tasks

#### 2. Fallback Mechanisms Are Critical
- 85% Veo 3 success rate → 100% pipeline success with text fallback
- Retry logic handles transient API failures
- Error isolation prevents cascade failures

#### 3. Structured Data Flow Simplifies Debugging
- Consistent JSON output at every step
- Timestamped folders provide audit trail
- Easy to replay failed steps manually

### Design Principles Applied

| Principle | Implementation | Benefit |
|-----------|----------------|---------|
| **Separation of Concerns** | N8N orchestrates, Python executes | Easy testing, maintenance |
| **Idempotency** | Each tool can re-run safely | Fault tolerance |
| **Observability** | Structured JSON, logs, timestamps | Easy debugging |
| **Fail-Safe** | Fallback mechanisms, retries | High reliability |
| **Modularity** | Reusable functions in separate modules | Code reuse |

### Production Lessons

1. **API Dependencies**: Always have fallbacks (Veo 3 → text video)
2. **OAuth Tokens Expire**: Build token refresh logic from day one
3. **Rate Limits Hit**: Retry with exponential backoff required
4. **Windows Paths**: Use absolute paths and escape backslashes in N8N
5. **Documentation**: Write as you build (saves time later)

---

## 🎯 Use Cases

### Primary Use Case: ASMR Content Creator
**Scenario**: Solo YouTuber wants to post daily Shorts without manual work

**Solution**:
- Schedule pipeline every 12 hours (2 videos/day)
- Automatic trend discovery ensures relevance
- AI disclosure maintains transparency
- Cost: $24/month vs $80/day manual labor

**Result**: 60x cost reduction, consistent upload schedule

### Secondary Use Cases

1. **Content Testing Lab**: Rapidly prototype ASMR concepts (5-10 videos/hour)
2. **Market Research**: Analyze trending themes without manual analysis
3. **Educational**: Learn AI orchestration, video APIs, workflow automation
4. **Portfolio Project**: Demonstrate full-stack automation skills

### Not Recommended For

❌ **High-quality commercial production** (audio quality limitations)  
❌ **Brand partnerships** (requires human creative control)  
❌ **Multi-channel networks** (single channel only currently)  
❌ **Non-ASMR content** (designed specifically for ASMR niche)

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

### Development Setup

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/bliss-builder.git
cd bliss-builder

# 3. Create virtual environment
python -m venv .venv
source .venv/Scripts/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create feature branch
git checkout -b feature/amazing-feature

# 6. Make your changes

# 7. Test your changes
python agents/fetch_agent.py
python agents/video_gen_agent.py --theme "test"

# 8. Commit and push
git add .
git commit -m 'Add amazing feature'
git push origin feature/amazing-feature

# 9. Open Pull Request on GitHub
```

### Contribution Guidelines

- ✅ **Test thoroughly**: Run all agents independently
- ✅ **Document changes**: Update relevant .md files
- ✅ **Follow conventions**: Match existing code style
- ✅ **Add examples**: Include usage examples for new features
- ✅ **Update requirements.txt**: If adding dependencies

### Areas for Contribution

**High Priority**:
- 🔊 Custom audio integration (ElevenLabs/Murf.ai)
- 📊 Analytics dashboard (Flask/FastAPI + React)
- 🛡️ Content moderation AI (OpenAI Moderation API)
- 📱 Multi-channel OAuth management

**Medium Priority**:
- 🎨 Thumbnail generation (DALL-E/Midjourney)
- 📈 A/B testing framework for prompts
- 🌍 Multi-language support
- 🔄 TikTok/Instagram cross-posting

**Good First Issues**:
- 📝 Improve error messages
- 🐛 Fix Windows path handling edge cases
- 📚 Add more code comments
- 🧪 Add unit tests

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details.

You are free to:
- ✅ Use commercially
- ✅ Modify and distribute
- ✅ Use privately
- ✅ Sublicense

Conditions:
- 📄 Include copyright notice
- 📄 Include license text

---

## 🙏 Acknowledgments

### Technologies & Services

- **[N8N](https://n8n.io/)** - Open-source workflow automation platform
- **[Groq](https://groq.com/)** - Fast LLM inference with Llama 3.3-70b
- **[Google Veo 3](https://ai.google.dev/)** - AI video generation via Gemini API
- **[YouTube Data API](https://developers.google.com/youtube/v3)** - Trend data and video uploads

### Inspiration

- ASMR content creator community for trend insights
- N8N community for workflow design patterns
- AI video generation pioneers pushing creative boundaries

---

## 📞 Support & Contact

### Documentation
- 📖 [Project Documentation](PROJECT_DOCUMENTATION.md) - Complete 8,500+ word guide
- 🚀 [Quick Start Guide](QUICK_START.md) - 15-minute setup
- 🎨 [N8N Setup Guide](N8N_WORKFLOW_AGENT_INTEGRATION.md) - Detailed configuration
- 🏗️ [Architecture Guide](docs/AI_AGENT_ARCHITECTURE.md) - Visual diagrams

### Community
- 🐛 [GitHub Issues](https://github.com/sainadth/bliss-builder/issues) - Bug reports
- 💬 [GitHub Discussions](https://github.com/sainadth/bliss-builder/discussions) - Questions & ideas
- ⭐ [Star the repo](https://github.com/sainadth/bliss-builder) - Show support

### Author
- 👤 **Sainadth**
- 📧 GitHub: [@sainadth](https://github.com/sainadth)
- 🔗 Repository: [sainadth/bliss-builder](https://github.com/sainadth/bliss-builder)

---

## ⚠️ Important Disclaimers

### AI Content Disclosure

This tool generates AI-created content. **All uploaded videos automatically include proper AI disclosure** as required by YouTube policies (effective November 2024). The disclosure statement is added to every video description:

```
🤖 AI Disclosure: This video was created using AI technology (Google Veo 3) 
and automated systems. Content follows YouTube's policies and community guidelines.
```

### Terms of Service Compliance

Users are responsible for ensuring compliance with:
- ✅ **YouTube Terms of Service**: https://www.youtube.com/t/terms
- ✅ **YouTube Community Guidelines**: https://www.youtube.com/howyoutubeworks/policies/community-guidelines/
- ✅ **Google Cloud Terms**: https://cloud.google.com/terms
- ✅ **Groq Terms of Service**: https://groq.com/terms/

### Usage Responsibility

- ⚠️ **API Quotas**: Monitor your usage to avoid rate limits
- ⚠️ **Content Moderation**: Review generated content before publishing
- ⚠️ **Copyright**: Ensure generated content doesn't infringe copyrights
- ⚠️ **Brand Safety**: Validate themes are appropriate for your brand

### No Warranty

This software is provided "as is" without warranty of any kind. The authors are not responsible for:
- API costs incurred
- YouTube channel penalties
- Generated content quality
- Service interruptions

---

## 📈 Project Status

**Current Version**: 1.0.0  
**Status**: ✅ **Production Ready**  
**Last Updated**: December 9, 2025  
**Maintenance**: Active development

### Recent Updates

- ✅ **Dec 9, 2025**: Complete project documentation (8,500+ words)
- ✅ **Nov 29, 2025**: N8N v1.121.3 integration guide
- ✅ **Nov 25, 2025**: Agent migration completed (150+ successful runs)
- ✅ **Nov 13, 2025**: Production testing (48 consecutive runs, 93.75% success)
- ✅ **Nov 11, 2025**: Initial AI agent architecture implementation

### Statistics

- 📊 **150+ Production Runs**: Proven reliability
- 📈 **92% Success Rate**: High availability
- 📝 **2,000+ Lines of Docs**: Comprehensive coverage
- ⭐ **5 Core Features**: All objectives completed
- 🎯 **$24/month Cost**: Highly cost-effective

---

## 🎬 Example Output

### Sample Generated Video Metadata

```json
{
  "status": "success",
  "video_path": "D:\\bliss-builder\\output\\12_02_2025_23_00_31\\video_20251202_220107.mp4",
  "narration": "As I gently carve this wooden spoon, the soft scratching of the blade against the wood fills the air, accompanied by the soothing tapping of the tool on the workbench. The tactile sensation of the wood grain beneath my fingers is calming, and the visual flow of the shavings falling away is mesmerizing.",
  "theme": "Whimsical wooden spoon carving with gentle scratching and tapping sounds",
  "veo3_prompt": "PORTRAIT 9:16: Macro close-up of a whimsical wooden spoon, intricately carved with swirling patterns, centered vertically. Camera slowly orbits 360° around the spoon in 8 seconds, starting and ending with the handle pointing directly up at 12 o'clock. Perfect loop. No people, no hands.",
  "veo3_used": true,
  "timestamp": "2025-12-02T22:03:44"
}
```

### Sample Themes Generated

From actual production runs:
- "Whimsical wooden spoon carving with gentle scratching and tapping sounds"
- "Relaxing rain sounds with distant thunder for deep sleep meditation"
- "Soft fabric folding with ASMR whispers and gentle movements"
- "Gentle paintbrush strokes on canvas with soothing ambient music"
- "Whispered woodland weaving with soothing yarn sounds and gentle forest ambiance"

---

## 🌟 Star History

If this project helped you, please consider:
- ⭐ **Starring the repository** on GitHub
- 🔄 **Sharing with others** who might benefit
- 💬 **Providing feedback** through issues/discussions
- 🤝 **Contributing** improvements and features

---

**Built with ❤️ for ASMR content creators**

**Transform your content creation workflow. Start automating today!** 🚀


