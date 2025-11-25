# Agent Migration Plan - Bliss Builder

This document outlines the step-by-step plan to migrate your N8N workflow from direct Python scripts to LangChain agents.

---

## 📋 Overview

**Goal**: Replace 3 N8N nodes (Fetch Agent, Video Generation Agent, Video Upload) with LangChain-powered agents that can reason and use tools.

**Timeline**: ~2.5 hours total

**Current State**: 
- ✅ Working Python scripts in `trend_fetching/`, `video_generation/`, `video_upload/`
- ✅ N8N workflow with Execute Command nodes
- ✅ APIs configured (YouTube, Groq, Gemini)

**Target State**:
- ✅ 3 separate agent files with tool-based orchestration
- ✅ Agents can be called from N8N or run standalone
- ✅ JSON output for easy integration
- ✅ Better error handling and logging

---

## 🏗️ Project Structure (After Migration)

```
d:\San\bliss-builder\
├── agents/
│   ├── __init__.py                  # NEW: Agent module initialization
│   ├── fetch_agent.py               # NEW: Trend fetching + theme extraction agent
│   ├── video_gen_agent.py           # NEW: Video generation agent
│   ├── upload_agent.py              # NEW: YouTube upload agent
│   └── README.md                    # NEW: Agent usage docs
├── trend_fetching/
│   └── trend_fetch.py               # KEEP: Reused by fetch_agent
├── video_generation/
│   └── generate_video.py            # KEEP: Reused by video_gen_agent
├── video_upload/
│   └── upload_to_youtube.py         # KEEP: Reused by upload_agent
├── output/
│   ├── trends/                      # JSON output from agents
│   ├── videos/                      # Generated videos
│   └── logs/                        # Agent execution logs
├── .env                             # API keys
├── requirements.txt                 # UPDATE: Add langchain dependencies
└── AGENT_MIGRATION_PLAN.md          # THIS FILE
```

---

## 📝 Migration Steps

### Phase 1: Setup (10 minutes)

#### Step 1.1: Install Dependencies

```powershell
# Navigate to project root
cd d:\San\bliss-builder

# Install LangChain and dependencies
pip install langchain langchain-groq langchain-community python-dotenv requests
```

#### Step 1.2: Update requirements.txt

```txt
# filepath: d:\San\bliss-builder\requirements.txt
google-api-python-client==2.108.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
groq==0.4.1
langchain==0.1.0
langchain-groq==0.0.1
langchain-community==0.0.10
python-dotenv==1.0.0
requests==2.31.0
```

#### Step 1.3: Create Agent Directory

```powershell
# Create agents directory
mkdir agents
New-Item agents\__init__.py -ItemType File
```

---

### Phase 2: Build Fetch Agent (30 minutes)

#### Step 2.1: Create Fetch Agent

**File**: `agents/fetch_agent.py`

**Purpose**: 
- Fetches ASMR trends using existing `trend_fetch.py` functions
- Extracts theme using Groq LLM
- Returns JSON output for N8N

**Key Features**:
- ✅ Reuses your existing `collect_trends_with_metadata()` function
- ✅ Reuses your existing `extract_theme_with_llm()` function
- ✅ Wraps them in LangChain Tool
- ✅ Outputs structured JSON

**Test Command**:
```powershell
python agents\fetch_agent.py
```

**Expected Output**:
```json
{
  "status": "success",
  "theme": "gentle cardboard crafting with satisfying crushing sounds",
  "trends_count": 50,
  "trends": [...]
}
```

---

### Phase 3: Build Video Generation Agent (45 minutes)

#### Step 3.1: Create Video Gen Agent

**File**: `agents/video_gen_agent.py`

**Purpose**:
- Generates ASMR narration from theme using Groq
- Calls Veo 3 API to generate 8-second video
- Handles polling for video completion
- Returns video URL

**Key Tools**:
1. `generate_narration` - Creates 2-3 sentence narration
2. `generate_video` - Calls Veo 3 wrapper API

**Requirements**:
- ⚠️ Requires Veo 3 wrapper API (deploy separately to Railway/Vercel)
- Alternative: Mock video generation for testing

**Test Command**:
```powershell
# Set test theme
$env:TEST_THEME="gentle rain over peaceful forest"
python agents\video_gen_agent.py
```

**Expected Output**:
```json
{
  "status": "success",
  "narration": "Soft raindrops cascade through emerald leaves...",
  "video_url": "https://storage.googleapis.com/...",
  "duration": 8
}
```

---

### Phase 4: Build Upload Agent (30 minutes)

#### Step 4.1: Create Upload Agent

**File**: `agents/upload_agent.py`

**Purpose**:
- Downloads generated video from URL
- Uploads to YouTube with metadata
- Returns video ID

**Key Features**:
- ✅ Reuses your existing `upload_to_youtube.py` functions
- ✅ Handles video download
- ✅ Cleans up temp files

**Test Command**:
```powershell
# Requires OAuth token from previous setup
python agents\upload_agent.py --video-url "https://test.mp4" --theme "test theme"
```

**Expected Output**:
```json
{
  "status": "success",
  "video_id": "dQw4w9WgXcQ",
  "upload_time": "2025-11-25T15:30:00Z"
}
```

---

### Phase 5: Update N8N Workflow (15 minutes)

#### Step 5.1: Replace Fetch Agent Node

**Current Node**: "Fetch Agent" (Execute Command)

**Replace With**:
- Node Type: Execute Command
- Command: `python`
- Arguments: `["d:\\San\\bliss-builder\\agents\\fetch_agent.py"]`
- Output Parsing: JSON

**Node Settings**:
```json
{
  "command": "python",
  "arguments": ["d:\\San\\bliss-builder\\agents\\fetch_agent.py"],
  "cwd": "d:\\San\\bliss-builder"
}
```

#### Step 5.2: Replace Video Generation Node

**Current Node**: "Video Generation Agent" (Execute Command)

**Replace With**:
- Command: `python`
- Arguments: Pass theme from previous node
- Add error handling for Veo 3 timeout

**Node Settings**:
```json
{
  "command": "python",
  "arguments": [
    "d:\\San\\bliss-builder\\agents\\video_gen_agent.py",
    "--theme",
    "={{$json.theme}}"
  ],
  "cwd": "d:\\San\\bliss-builder"
}
```

#### Step 5.3: Replace Upload Node

**Current Node**: "Video Upload" (Execute Command)

**Replace With**:
- Command: `python`
- Arguments: Pass video URL and metadata

**Node Settings**:
```json
{
  "command": "python",
  "arguments": [
    "d:\\San\\bliss-builder\\agents\\upload_agent.py",
    "--video-url",
    "={{$json.video_url}}",
    "--theme",
    "={{$json.theme}}",
    "--narration",
    "={{$json.narration}}"
  ],
  "cwd": "d:\\San\\bliss-builder"
}
```

---

### Phase 6: Testing & Validation (20 minutes)

#### Step 6.1: Test Individual Agents

```powershell
# Test 1: Fetch Agent
python agents\fetch_agent.py
# Expected: JSON with theme + trends

# Test 2: Video Gen Agent (mock mode)
python agents\video_gen_agent.py --theme "test theme" --mock
# Expected: JSON with narration + mock video URL

# Test 3: Upload Agent (dry run)
python agents\upload_agent.py --video-url "test.mp4" --theme "test" --dry-run
# Expected: JSON with simulated upload
```

#### Step 6.2: Test N8N Workflow

1. Open N8N workflow: `http://localhost:5678`
2. Click "Execute Workflow" (manual trigger)
3. Monitor each node execution
4. Verify JSON output at each step
5. Check final YouTube upload

#### Step 6.3: Validation Checklist

- [ ] Fetch Agent returns valid theme
- [ ] Theme is passed to Video Gen Agent
- [ ] Video Gen Agent returns video URL
- [ ] Upload Agent successfully uploads to YouTube
- [ ] Logs are written to `output/logs/`
- [ ] No API key errors
- [ ] Error handling works (test with invalid API key)

---

## 🚀 Deployment Options

### Option A: Keep N8N Local (Recommended for Start)

**Pros**:
- Zero deployment cost
- Direct access to local files
- Easy debugging

**Cons**:
- Requires computer to be on
- No remote access

**Setup**: Already done! Just run `n8n start`

---

### Option B: Migrate to N8N Cloud + Deploy Agents as APIs

**When to use**: After you've validated everything works locally

**Steps**:
1. Deploy agents to Railway/Vercel as REST APIs
2. Migrate N8N workflow to cloud
3. Replace Execute Command with HTTP Request nodes

**Cost**: ~$24-38/month (see `docs/N8N_WORKFLOW_CLOUD.md`)

---

## 🛠️ Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'langchain'"

**Solution**:
```powershell
pip install --upgrade langchain langchain-groq
```

### Issue: "GROQ_API_KEY not set"

**Solution**:
```powershell
# Check .env file
cat .env | Select-String "GROQ_API_KEY"

# If missing, add to .env
Add-Content .env "GROQ_API_KEY=your_key_here"
```

### Issue: Agent hangs during video generation

**Solution**:
- Check Veo 3 API wrapper logs
- Increase timeout in `video_gen_agent.py`
- Test with mock mode first

### Issue: YouTube upload fails with 403

**Solution**:
- Re-authenticate OAuth: `python video_upload\upload_to_youtube.py`
- Check token.json expiration
- Verify YouTube API quota

---

## 📚 Next Steps After Migration

1. **Add Monitoring**:
   - Log agent execution times
   - Track API usage
   - Set up alerts for failures

2. **Optimize Performance**:
   - Cache trend data (avoid re-fetching)
   - Parallel video generation (if generating multiple)
   - Batch YouTube uploads

3. **Add More Tools**:
   - Thumbnail generation agent
   - Analytics tracking agent
   - Social media cross-posting agent

4. **Scale to Production**:
   - Move to cloud deployment
   - Add retry logic with exponential backoff
   - Implement dead letter queue for failed uploads

---

## ✅ Success Criteria

Your migration is complete when:

- [ ] All 3 agents run successfully standalone
- [ ] N8N workflow executes end-to-end without errors
- [ ] Video is uploaded to YouTube automatically
- [ ] Logs show clear execution flow
- [ ] Error handling catches API failures gracefully
- [ ] You can schedule daily runs via N8N

---

## 📞 Support

If you encounter issues:

1. Check logs in `output/logs/`
2. Test individual agent scripts
3. Verify API keys in `.env`
4. Review N8N execution history
5. Check YouTube API quota: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas

---

**Estimated Total Time**: 2.5 hours
**Difficulty**: Intermediate
**Prerequisites**: Python, N8N, API keys configured

Good luck with your migration! 🚀