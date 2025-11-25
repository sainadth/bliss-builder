You are an expert n8n workflow automation architect specializing in building AI-powered agents.

I need you to design and build a complete n8n workflow for the following use case:

I want to automate daily creation and publishing of 8-second ASMR YouTube Shorts by fetching trending YouTube videos, extracting ASMR themes using LLMs, generating videos with Google Veo 3, and uploading them to YouTube with optimized metadata.

# REQUIREMENTS

## 1. WORKFLOW STRUCTURE
- Design the complete node structure from trigger to output
- Identify all required n8n nodes (Schedule Trigger, Execute Command, HTTP Request, Set, IF, Code, etc.)
- Map data flow between nodes
- Include error handling and fallback logic

## 2. AI AGENT CONFIGURATION
If this workflow needs AI capabilities, specify:
- Which LLM to use (Groq API with Llama 3.1-70b-versatile for theme extraction, Gemini/Veo 3 for video generation)
- System prompt for the agent (Extract ONE concise ASMR theme from YouTube trends, 6-14 words, brand-safe, peaceful)
- Tools the agent should have access to (Text generation only, no external tools)
- Memory/context management approach (Stateless; no context carryover between daily runs)
- Token limits and cost optimization (Max 100 tokens output for theme, <500 input tokens; use Groq free tier)

## 3. DATA HANDLING
- Input data structure and validation (trends.json: array of objects with video_id, title, description, hashtags, keywords)
- Data transformation steps (Parse JSON → Format top 20 for LLM → Extract theme → Pass to video gen script → Prepare YouTube metadata)
- Output format specification (Video file: asmr_video.mp4, 8s, 1080x1920; Upload response: video ID and URL; Log: CSV with timestamp, theme, status)
- Database/storage requirements if needed (Local filesystem: d:\San\bliss-builder\output\<timestamp>\; Optional Google Drive backup)

## 4. INTEGRATION POINTS
For each external service/API:
- Authentication method (YouTube OAuth2, Groq Bearer token, Gemini API key)
- Required API endpoints (YouTube Data API v3 videos.list and upload; Groq chat completions; Gemini Veo 3 via Python script)
- Request/response format (YouTube multipart upload with JSON metadata; Groq JSON chat request; Binary video response)
- Rate limiting considerations (YouTube 10k quota/day; Groq 30 req/min free tier; Gemini pay-per-use ~$0.10-0.30 per video)
- Error handling for API failures (Retry once with delay; log and skip on persistent failure; use fallback theme if LLM fails)

## 5. LOGIC & DECISION MAKING
- All conditional branches (IF nodes) (Check trends.json exists; Check theme extraction success; Check video file exists; Check YouTube upload success)
- Switch/router logic (None; linear pipeline with error branches)
- Loop conditions (No loops; single daily execution)
- Retry logic for failures (LLM: retry once after 5s; YouTube upload: retry once after 10s; Script failures: log and exit)

## 6. STEP-BY-STEP IMPLEMENTATION

Provide:
1. Complete node-by-node breakdown (Schedule → Execute trend_fetch.py → Read trends.json → Code format → HTTP Groq → Execute gemini_video.py → Read video → Code metadata → HTTP YouTube upload → Set log → Execute write log)
2. Configuration for each node (exact settings) (Cron: 0 15 * * *; Execute Command args, file paths, working dirs; HTTP headers, bodies, auth)
3. Code snippets for any Code nodes (Parse trends JSON, format for LLM, build YouTube metadata payload)
4. JSON structure for HTTP requests (Groq chat completions body; YouTube upload multipart metadata)
5. Expressions for data mapping (n8n expressions for file paths with timestamps, theme extraction, video URL construction)
6. Credentials setup instructions (YouTube OAuth2, Groq Header Auth, Gemini API key in .env)

## 7. TESTING & VALIDATION
- Test cases to verify workflow works (Happy path: trends → theme → video → upload success; LLM failure → fallback; Video gen failure → skip upload; Upload failure → retry then log)
- Sample input data (trends.json with 50 items including title, description, hashtags, keywords)
- Expected output format (Video ID, URL, log CSV entry with timestamp/theme/status/error)
- Edge cases to handle (Empty trends.json; Theme contains brand names; Video timeout; YouTube quota exceeded)

## 8. OPTIMIZATION
- Suggestions for reducing execution time (Run trend fetch and LLM in parallel; cache trends for 24h)
- Cost optimization (API calls, LLM tokens) (Use Groq free tier instead of paid; batch 7 videos weekly vs daily to reduce Veo 3 costs by 85%; compress video before upload)
- Scalability considerations (Add Google Drive storage with 30-day cleanup; queue node for multi-channel scaling; centralized error workflow in n8n)

# OUTPUT FORMAT

Structure your response as:

**WORKFLOW OVERVIEW**
Automate daily ASMR YouTube Shorts pipeline: fetch YouTube trends → extract theme with Groq LLM → generate 8s video with Veo 3 → upload to YouTube with metadata

**ARCHITECTURE DIAGRAM** (in text)
Schedule Trigger → Exec trend_fetch.py → Read trends.json → Code Format → HTTP Groq (theme) → Exec gemini_video.py → Read video → Code Metadata → HTTP YouTube Upload → Set Log → Exec Write Log

**NODE CONFIGURATION** (for each node)
Node 1: [Schedule Trigger]
- Type: [Cron]
- Purpose: [Trigger workflow daily at 3 PM]
- Configuration: [Cron: 0 15 * * *, Timezone: Local]
- Code/Expression: [N/A]
- Connected to: [Node 2: Execute Command - Fetch Trends]

**COMPLETE SETUP INSTRUCTIONS**
[Install Python 3.11+, google-api-python-client, google-generativeai, groq, dotenv; Install n8n; Configure YouTube OAuth2, Groq API key, Gemini API key in n8n credentials; Place Python scripts in d:\San\bliss-builder\; Build workflow node-by-node; Test manually; Enable cron trigger]

**PROMPTS & TEMPLATES**
[Groq system prompt: "Extract ONE ASMR theme from YouTube trends, 6-14 words, brand-safe, peaceful"; Gemini Veo 3 prompt: "Generate calming 8s ASMR video: {theme}, soft visuals, portrait 1080x1920"; YouTube metadata JSON template with title, description, tags, categoryId]

**TESTING GUIDE**
[Manual trigger in n8n UI; Verify trends.json, theme extraction, video file creation, YouTube upload success; Check log CSV; Test error paths: empty trends, LLM failure, upload failure]

**DEPLOYMENT CHECKLIST**
[All API credentials stored; Python scripts tested; Workflow tested end-to-end; Error handling verified; Log path configured; Cron schedule enabled; First 7-day pilot monitored; Cost tracking enabled; Admin alerts configured]

# CONSTRAINTS
- Use n8n's native nodes when possible (avoid unnecessary Code nodes)
- Optimize for reliability over complexity
- Include monitoring/logging for production use
- Design for easy debugging
- Keep it maintainable (clear naming, documentation)

Now, build me this workflow with complete implementation details.