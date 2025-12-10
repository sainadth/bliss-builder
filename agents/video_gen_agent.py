"""
Video Generation Agent - Bliss Builder

This agent generates ASMR video narration and creates videos using LangChain.
Reuses existing gemini_video.py functions.

Usage:
    python agents/video_gen_agent.py --theme "gentle rain sounds"
    python agents/video_gen_agent.py --theme "soft cardboard tapping" --output-file output/videos/latest.json
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
from langchain_groq import ChatGroq

from video_generation.gemini_video import (
    generate_veo3_prompt_with_gemini,
    generate_video_with_veo3,
    render_frames,
    assemble_video
)

dotenv.load_dotenv()


def generate_narration_tool(theme: str) -> dict:
    """Generate ASMR video narration using Groq LLM."""
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        return {"status": "error", "error": "GROQ_API_KEY not set in .env"}
    
    try:
        print(f"🎨 Generating narration for theme: {theme}", flush=True)
        
        client = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            api_key=groq_api_key
        )
        
        prompt = f"""Create a 2-3 sentence ASMR video narration for this theme: "{theme}"

Requirements:
- Include sensory details (visual, auditory, tactile)
- Peaceful, calming, soothing tone
- Should take about 8 seconds when spoken slowly
- Optimized for vertical video (9:16 portrait format)
- Safe for all audiences, no controversial content
- Focus on the calming, meditative aspects

Output ONLY the narration text (no additional commentary)."""
        
        response = client.invoke([{"role": "user", "content": prompt}])
        narration = response.content.strip()
        
        print(f"✅ Narration generated: {narration[:100]}...", flush=True)
        
        return {
            "status": "success",
            "narration": narration,
            "theme": theme
        }
        
    except Exception as e:
        print(f"❌ Error generating narration: {str(e)}", file=sys.stderr, flush=True)
        return {"status": "error", "error": str(e)}


def generate_video_tool(narration_data: dict, output_file: str = None) -> dict:
    """Generate video using Veo 3 from narration."""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not gemini_api_key:
        return {"status": "error", "error": "GEMINI_API_KEY not set in .env"}
    
    narration = narration_data.get("narration", "")
    theme = narration_data.get("theme", "")
    
    if not narration or not theme:
        return {"status": "error", "error": "Missing narration or theme"}
    
    try:
        print("🎬 Generating Veo 3 prompt...", flush=True)
        
        # Generate Veo 3 prompt from narration
        veo3_prompt = generate_veo3_prompt_with_gemini(
            theme=theme,
            trends=[],  # Not using trends for individual video generation
            api_key=gemini_api_key
        )
        
        print(f"📝 Veo 3 Prompt: {veo3_prompt[:200]}...", flush=True)
        
        # Create output directory
        # If output_file is provided, use its directory. Otherwise default to output/videos
        if output_file:
            output_dir = Path(output_file).parent
        else:
            output_dir = Path("output/videos")
            
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"video_{timestamp}.mp4"
        
        print("🎥 Generating video with Veo 3 (this may take 5-10 minutes)...", flush=True)
        
        # Generate video with Veo 3
        video_path = generate_video_with_veo3(
            veo3_prompt=veo3_prompt,
            api_key=gemini_api_key,
            duration=8,
            output_path=str(output_path)
        )
        
        if video_path and os.path.exists(video_path):
            print(f"✅ Video generated successfully: {video_path}", flush=True)
            
            return {
                "status": "success",
                "video_path": str(video_path),
                "narration": narration,
                "theme": theme,
                "veo3_prompt": veo3_prompt,
                "veo3_used": True,
                "timestamp": datetime.now().isoformat()
            }
        else:
            print("⚠️ Veo 3 generation failed (likely quota exhausted), using fallback text-based video...", flush=True)
            print("💡 Tip: Check your Gemini API quota at https://ai.dev/usage", flush=True)
            
            # Fallback: Create text-based video
            frames = render_frames([narration], size=(1080, 1920))
            fallback_path = output_dir / f"video_fallback_{timestamp}.mp4"
            
            assemble_video(frames, str(fallback_path), total_duration=8, fps=24)
            
            return {
                "status": "success",
                "video_path": str(fallback_path),
                "narration": narration,
                "theme": theme,
                "fallback": True,
                "veo3_used": False,
                "note": "Used text-based fallback (Veo 3 quota exhausted or unavailable)",
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        print(f"❌ Error generating video: {str(e)}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


def run_video_gen_agent(theme: str, output_file: str = None):
    """Main entry point for video generation agent."""
    # Redirect stdout to stderr to keep the output clean for N8N
    # Only the final JSON should be on stdout
    original_stdout = sys.stdout
    sys.stdout = sys.stderr

    print("=" * 60, flush=True)
    print("🤖 VIDEO GENERATION AGENT STARTING", flush=True)
    print("=" * 60, flush=True)
    print(f"🎯 Theme: {theme}", flush=True)
    
    try:
        # For simpler execution, call tools directly instead of agent
        # This avoids complex agent reasoning for sequential tasks
        
        # Step 1: Generate narration
        print("\n📝 Step 1: Generating narration...", flush=True)
        narration_result = generate_narration_tool(theme)
        
        if narration_result.get("status") != "success":
            raise Exception(f"Narration generation failed: {narration_result.get('error')}")
        
        # Step 2: Generate video
        print("\n🎬 Step 2: Generating video...", flush=True)
        video_result = generate_video_tool(narration_result, output_file)
        
        if video_result.get("status") != "success":
            raise Exception(f"Video generation failed: {video_result.get('error')}")
        
        print("\n" + "=" * 60, flush=True)
        print("✅ VIDEO GENERATION AGENT COMPLETED", flush=True)
        print("=" * 60, flush=True)
        
        # Save metadata if output file specified
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(video_result, f, indent=2)
            print(f"📁 Metadata saved to: {output_file}", flush=True)
        
        # Print summary
        print(f"\n🎬 Video Path: {video_result.get('video_path', 'N/A')}", flush=True)
        print(f"📝 Narration: {video_result.get('narration', 'N/A')}", flush=True)
        
        if video_result.get("fallback"):
            print("⚠️ Note: Used fallback text-based video", flush=True)
        
        # Create a cleaner output for N8N
        n8n_output = {
            "status": video_result.get("status"),
            "video_path": video_result.get("video_path"),
            "theme": video_result.get("theme"),
            "timestamp": video_result.get("timestamp"),
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
            "theme": theme,
            "timestamp": datetime.now().isoformat()
        }
        print("\n" + json.dumps(error_data, indent=2), file=sys.stderr, flush=True)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate ASMR video from theme")
    parser.add_argument(
        "--theme",
        type=str,
        required=True,
        help="ASMR theme for video generation"
    )
    parser.add_argument(
        "--output-file",
        type=str,
        help="Path to save JSON metadata (optional)"
    )
    
    args = parser.parse_args()
    
    run_video_gen_agent(theme=args.theme, output_file=args.output_file)
