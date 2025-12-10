"""
Fetch Agent - Bliss Builder

This agent fetches ASMR trending videos and extracts themes using LangChain.
Reuses existing trend_fetch.py functions.

Usage:
    python agents/fetch_agent.py
    python agents/fetch_agent.py --output-file output/trends/latest.json
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
import sys
import io

# Force UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

import dotenv

from trend_fetching.trend_fetch import collect_trends_with_metadata, extract_theme_with_llm

dotenv.load_dotenv()


def fetch_trends_tool(input_data: str, max_retries: int = 3) -> dict:
    """Fetches ASMR trends and extracts theme using Groq LLM."""
    youtube_api_key = os.getenv("YOUTUBE_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not youtube_api_key:
        return {"status": "error", "error": "YOUTUBE_API_KEY not set in .env"}
    
    if not groq_api_key:
        return {"status": "error", "error": "GROQ_API_KEY not set in .env"}
    
    # Retry logic for API failures
    for attempt in range(max_retries):
        try:
            print(f"🔍 Fetching ASMR trends from YouTube... (Attempt {attempt + 1}/{max_retries})", flush=True)
            
            # Fetch trends using existing function
            trends = collect_trends_with_metadata(
                youtube_api_key=youtube_api_key,
                region="US",
                max_results=50
            )
            
            if not trends:
                return {"status": "error", "error": "No trends found"}
            
            print(f"✅ Found {len(trends)} trending ASMR videos", flush=True)
            print("🎨 Extracting creative theme...", flush=True)
            
            # Extract theme using existing function
            theme = extract_theme_with_llm(trends, groq_api_key)
            
            print(f"✨ Theme extracted: {theme}", flush=True)
            
            return {
                "status": "success",
                "theme": theme,
                "trends_count": len(trends),
                "top_trends": trends[:5],  # Return top 5 for context
                "all_trends": trends,  # Keep all for downstream processing
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {str(e)}", file=sys.stderr, flush=True)
            if attempt < max_retries - 1:
                import time
                wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, 6s
                print(f"⏳ Waiting {wait_time}s before retry...", flush=True)
                time.sleep(wait_time)
            else:
                print(f"❌ All {max_retries} attempts failed", file=sys.stderr, flush=True)
                return {"status": "error", "error": f"Failed after {max_retries} attempts: {str(e)}"}


def run_fetch_agent(output_file: str = None):
    """Main entry point for the fetch agent."""
    # Redirect stdout to stderr to keep the output clean for N8N
    # Only the final JSON should be on stdout
    original_stdout = sys.stdout
    sys.stdout = sys.stderr

    print("=" * 60, flush=True)
    print("🤖 FETCH AGENT STARTING", flush=True)
    print("=" * 60, flush=True)
    
    try:
        # Call the tool function directly
        result_data = fetch_trends_tool("fetch trends")
        
        print("\n" + "=" * 60, flush=True)
        print("✅ FETCH AGENT COMPLETED", flush=True)
        print("=" * 60, flush=True)
        
        # Save to file if specified
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(result_data, f, indent=2)
            print(f"📁 Results saved to: {output_file}", flush=True)
        
        # Print summary
        if isinstance(result_data, dict) and result_data.get("status") == "success":
            print(f"\n🎯 Theme: {result_data.get('theme', 'N/A')}", flush=True)
            print(f"📊 Trends Found: {result_data.get('trends_count', 0)}", flush=True)
        
        # Create a cleaner output for N8N (exclude massive trends list)
        n8n_output = {
            "status": result_data.get("status"),
            "theme": result_data.get("theme"),
            "trends_count": result_data.get("trends_count"),
            "timestamp": result_data.get("timestamp"),
            "output_file": output_file  # Pass the file path so next nodes can find the full data
        }
        
        # Restore stdout for the final JSON output
        sys.stdout = original_stdout
        # Always output JSON to stdout for N8N parsing
        print("\n" + json.dumps(n8n_output, indent=2), flush=True)
        
        return n8n_output
        
    except Exception as e:
        # Restore stdout just in case
        sys.stdout = original_stdout
        error_data = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print("\n" + json.dumps(error_data, indent=2), file=sys.stderr, flush=True)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch ASMR trends and extract theme")
    parser.add_argument(
        "--output-file",
        type=str,
        help="Path to save JSON output (optional)"
    )
    
    args = parser.parse_args()
    
    run_fetch_agent(output_file=args.output_file)
