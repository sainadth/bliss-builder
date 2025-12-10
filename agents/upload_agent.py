"""
Upload Agent - Bliss Builder

This agent uploads generated videos to YouTube with proper metadata using LangChain.
Reuses existing youtube_upload.py functions.

Usage:
    python agents/upload_agent.py --video-path output/videos/video.mp4 --theme "gentle rain" --narration "Soft raindrops..."
    python agents/upload_agent.py --video-path output/videos/video.mp4 --theme "cardboard tapping" --privacy unlisted
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
import io

# Force UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

import dotenv

from video_upload.youtube_upload import upload_youtube_short, get_authenticated_service

dotenv.load_dotenv()


def upload_to_youtube_tool(video_data: dict) -> dict:
    """Upload video to YouTube with metadata."""
    video_path = video_data.get("video_path")
    theme = video_data.get("theme")
    narration = video_data.get("narration", "")
    privacy = video_data.get("privacy", "public")
    
    if not video_path:
        return {"status": "error", "error": "Missing video_path"}
    
    if not theme:
        return {"status": "error", "error": "Missing theme"}
    
    if not os.path.exists(video_path):
        return {"status": "error", "error": f"Video file not found: {video_path}"}
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"📤 Uploading video to YouTube... (Attempt {attempt + 1}/{max_retries})", flush=True)
            print(f"   Video: {video_path}", flush=True)
            print(f"   Theme: {theme}", flush=True)
            print(f"   Privacy: {privacy}", flush=True)
            
            # Authenticate YouTube service first
            print("🔐 Authenticating with YouTube...", flush=True)
            youtube_service = get_authenticated_service()
            
            # Upload using existing function
            result = upload_youtube_short(
                video_path=video_path,
                theme=theme,
                narration=narration,
                privacy=privacy
            )
            
            print(f"✅ Upload successful!", flush=True)
            print(f"   Video ID: {result['video_id']}", flush=True)
            print(f"   URL: {result['video_url']}", flush=True)
            
            return {
                "status": "success",
                "video_id": result["video_id"],
                "video_url": result["video_url"],
                "title": result["title"],
                "privacy": result["privacy"],
                "timestamp": datetime.now().isoformat(),
                "theme": theme,
                "ai_disclosed": result.get("ai_disclosed", True),
                "upload_attempts": attempt + 1
            }
            
        except Exception as e:
            print(f"⚠️ Upload attempt {attempt + 1} failed: {str(e)}", file=sys.stderr, flush=True)
            if attempt < max_retries - 1:
                import time
                wait_time = (attempt + 1) * 3  # Exponential backoff: 3s, 6s, 9s
                print(f"⏳ Waiting {wait_time}s before retry...", flush=True)
                time.sleep(wait_time)
            else:
                print(f"❌ All {max_retries} upload attempts failed", file=sys.stderr, flush=True)
                import traceback
                traceback.print_exc()
                return {"status": "error", "error": f"Upload failed after {max_retries} attempts: {str(e)}"}


def run_upload_agent(video_path: str, theme: str, narration: str = None, privacy: str = "public", output_file: str = None):
    """Main entry point for upload agent."""
    # Redirect stdout to stderr to keep the output clean for N8N
    # Only the final JSON should be on stdout
    original_stdout = sys.stdout
    sys.stdout = sys.stderr

    print("=" * 60, flush=True)
    print("🤖 UPLOAD AGENT STARTING", flush=True)
    print("=" * 60, flush=True)
    
    try:
        # For simpler execution, call tool directly
        video_data = {
            "video_path": video_path,
            "theme": theme,
            "narration": narration or "",
            "privacy": privacy
        }
        
        result = upload_to_youtube_tool(video_data)
        
        if result.get("status") != "success":
            raise Exception(f"Upload failed: {result.get('error')}")
        
        print("\n" + "=" * 60, flush=True)
        print("✅ UPLOAD AGENT COMPLETED", flush=True)
        print("=" * 60, flush=True)
        
        # Save to file if specified
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"📁 Results saved to: {output_file}", flush=True)
        
        # Print summary
        print(f"\n🎬 Video URL: {result.get('video_url', 'N/A')}", flush=True)
        print(f"🆔 Video ID: {result.get('video_id', 'N/A')}", flush=True)
        print(f"📝 Title: {result.get('title', 'N/A')}", flush=True)
        
        # Create a cleaner output for N8N
        n8n_output = {
            "status": result.get("status"),
            "video_url": result.get("video_url"),
            "video_id": result.get("video_id"),
            "timestamp": result.get("timestamp"),
            "output_file": output_file
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
            "video_path": video_path,
            "theme": theme,
            "timestamp": datetime.now().isoformat()
        }
        print("\n" + json.dumps(error_data, indent=2), file=sys.stderr, flush=True)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload video to YouTube")
    parser.add_argument(
        "--video-path",
        type=str,
        required=True,
        help="Path to video file to upload"
    )
    parser.add_argument(
        "--theme",
        type=str,
        required=True,
        help="ASMR theme for video title/description"
    )
    parser.add_argument(
        "--narration",
        type=str,
        help="Video narration text (optional)"
    )
    parser.add_argument(
        "--privacy",
        type=str,
        choices=["public", "unlisted", "private"],
        default="public",
        help="YouTube privacy setting (default: public)"
    )
    parser.add_argument(
        "--output-file",
        type=str,
        help="Path to save JSON output (optional)"
    )
    
    args = parser.parse_args()
    
    run_upload_agent(
        video_path=args.video_path,
        theme=args.theme,
        narration=args.narration,
        privacy=args.privacy,
        output_file=args.output_file
    )
