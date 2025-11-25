BLISS BUILDER - IMPLEMENTATION PLAN

CURRENT IMPLEMENTATION

Bliss Builder automates YouTube Shorts creation through three stages: Trend Fetching (discovers ASMR topics via YouTube API + Groq LLM), Video Generation (creates 8s looping videos with Gemini + Veo 3), and YouTube Upload (publishes with AI disclosure). Currently uses n8n workflow with Execute Command nodes calling Python scripts directly via subprocess. Main limitations: no retry logic, basic error handling, tight coupling between components, and no graceful degradation when APIs fail.

WHAT NEEDS TO BE ADDED

1. Agent-Based Architecture (Replacing Execute Command Nodes)

Refactor existing Python scripts into reusable Agent classes that n8n Execute Command nodes will call. Each agent wraps existing script logic with enhanced error handling, input validation, and structured JSON output. Agents run as standalone Python scripts but return consistent JSON responses that n8n can parse. No HTTP/API needed - n8n Execute Command nodes will directly invoke: python agents/trend_fetch_agent.py, python agents/video_generation_agent.py, python agents/upload_agent.py.

2. Comprehensive Error Handling

Implement four error categories with exit codes: TRANSIENT (exit code 2, retry immediately - network timeouts, token expiry), RATE_LIMIT (exit code 3, exponential backoff - API quotas), DEGRADED (exit code 0 with warning in JSON, use fallback - Veo 3 to text slides, Groq to keywords), FATAL (exit code 1, stop pipeline - invalid credentials). Add retry decorators with exponential backoff, structured JSON logging with correlation IDs, and automatic fallback mechanisms for each agent. All output via stdout as JSON for n8n parsing.

IMPLEMENTATION PRIORITY

Phase 1 (Week 1-2): Refactor existing scripts into agent classes with consistent JSON output format. Each agent accepts CLI arguments, executes logic, handles errors, and prints JSON result to stdout for n8n to parse.

Phase 2 (Week 3): Add retry logic inside agents using decorators, implement error classification with proper exit codes, add structured logging to files, and automatic fallback mechanisms that still return success JSON.

Phase 3 (Week 4): Update n8n Execute Command nodes to call new agent scripts, test end-to-end workflow, add error handling in n8n using exit codes, optimize performance.


