import os
import sys
import json
import argparse
import dotenv
import time
from google import genai
from google.genai import types
from groq import Groq

from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, concatenate_videoclips

dotenv.load_dotenv()

def _fail(msg: str):
    """Print error and exit."""
    print(f"ERROR: {msg}", file=sys.stderr, flush=True)
    sys.exit(1)

def generate_veo3_prompt_with_gemini(theme: str, trends: list, api_key: str):
    """Use Gemini AI to generate a COMPLETE, CREATIVE Veo 3 prompt for 8-second looping PORTRAIT ASMR video."""
    if not api_key:
        print("Warning: No GEMINI_API_KEY, using fallback prompt generation.", flush=True)
        return _fallback_veo3_prompt(theme)
    
    try:
        import random
        
        client = genai.Client(api_key=api_key)
        
        # Extract context from trending videos
        context_keywords = []
        for item in trends[:10]:
            context_keywords.extend(item.get("keywords", [])[:3])
            context_keywords.extend(item.get("hashtags", [])[:2])
        
        unique_keywords = list(dict.fromkeys(context_keywords))[:10]
        keywords_str = ", ".join(unique_keywords)
        
        # Random creative directions
        visual_styles = ["macro close-up photography", "slow-motion cinematic", "smooth dolly shot", 
                        "orbital camera movement", "first-person POV perspective", "top-down bird's eye view"]
        color_palettes = ["soft pastels with dreamy lighting", "muted earth tones with warm ambiance",
                         "cool blues and greens with tranquil mood", "monochromatic with subtle gradients"]
        motion_types = ["360-degree slow rotation", "gentle oscillating zoom in and out",
                       "smooth circular orbit around subject", "rhythmic pulsing expansion and contraction"]
        
        chosen_visual = random.choice(visual_styles)
        chosen_palette = random.choice(color_palettes)
        chosen_motion = random.choice(motion_types)
        
        prompt = (
            f"You are a creative video director specializing in ASMR content for YouTube Shorts. "
            f"Create a COMPLETE prompt for Veo 3 AI to generate an 8-second seamless looping ASMR video.\n\n"
            f"Theme: {theme}\n"
            f"Context: {keywords_str}\n\n"
            f"SEAMLESS LOOPING REQUIREMENTS:\n"
            f"- Camera MUST complete full cycle and return to EXACT starting position in 8 seconds\n"
            f"- Use CIRCULAR motion only (no linear pans/tilts)\n"
            f"- Objects in same position at start and end\n\n"
            f"PORTRAIT FORMAT REQUIREMENTS:\n"
            f"- VERTICAL 9:16 aspect ratio (1080x1920)\n"
            f"- Optimize for mobile viewing\n"
            f"- Center subject in portrait orientation\n\n"
            f"SPECS:\n"
            f"- Camera motion: {chosen_motion}\n"
            f"- Visual style: {chosen_visual}\n"
            f"- Color palette: {chosen_palette}\n"
            f"- Duration: exactly 8 seconds\n"
            f"- NO text overlays, NO people (unless abstract/distant)\n\n"
            f"EXAMPLE: 'PORTRAIT 9:16: Macro close-up of pink kinetic sand centered vertically. "
            f"Camera orbits 360° in 8 seconds, starting/ending at 12 o'clock. Soft pastel lighting. Perfect loop.'\n\n"
            f"Output ONLY the Veo 3 prompt (one paragraph)."
        )
        
        print("Generating Veo 3 prompt with Gemini...", flush=True)
        
        model = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )
        
        veo3_prompt = model.text.strip()
        
        if veo3_prompt and len(veo3_prompt) > 100:
            return veo3_prompt
        else:
            return _fallback_veo3_prompt(theme)
            
    except Exception as e:
        print(f"Warning: Veo 3 prompt generation failed ({e}), using fallback.", flush=True)
        return _fallback_veo3_prompt(theme)

def _fallback_veo3_prompt(theme: str):
    """Generate simple fallback Veo 3 prompt (config handles technical specs)."""
    import random
    
    motions = [
        "Camera orbits 360° around subject in 8 seconds, returning to exact start position for perfect loop",
        "Smooth zoom in for 4s then zoom out for 4s, creating seamless breathing loop cycle",
        "Camera rotates clockwise, completing one full 360° rotation in 8 seconds for continuous loop"
    ]
    
    return (
        f"Cinematic ASMR close-up of {theme}. {random.choice(motions)}. "
        f"Soft dreamy lighting, shallow depth of field creating bokeh effect. "
        f"Professional cinematography with gentle, meditative movements. "
        f"Crystal clear details, no compression artifacts. "
        f"Peaceful, calming atmosphere perfect for meditation and relaxation. "
        f"Seamless loop optimized for YouTube Shorts."
    )

def generate_video_with_veo3(veo3_prompt: str, api_key: str, duration: int = 8, output_path: str = "temp_veo3_video.mp4"):
    """Use Google Veo 3 API to generate SEAMLESS LOOPING PORTRAIT video."""
    if not api_key:
        print("WARNING: No GEMINI_API_KEY, cannot use Veo 3.", flush=True)
        return None
    
    try:
        print(f"Initializing Veo 3 client...", flush=True)
        client = genai.Client(api_key=api_key)
        
        # CHECK 1: List available models
        print("Checking available models...", flush=True)
        try:
            all_models = list(client.models.list())
            model_names = [m.name for m in all_models]
            print(f"Total models available: {len(model_names)}", flush=True)
            
            veo_models = [m for m in model_names if 'veo' in m.lower()]
            if veo_models:
                print(f"VEO 3 FOUND: {veo_models}", flush=True)
            else:
                print("ERROR: No Veo models found!", flush=True)
                print("Your API key doesn't have Veo 3 access", flush=True)
                print("Request access at: https://aistudio.google.com/", flush=True)
                return None
        except Exception as e:
            print(f"ERROR: Cannot list models: {e}", flush=True)
            return None
        
        # Enhanced prompt
        enhanced_prompt = (
            f"{veo3_prompt}\n\n"
            f"CREATIVE REQUIREMENTS:\n"
            f"- VERTICAL 9:16 PORTRAIT FORMAT (1080x1920) REQUIRED for YouTube Shorts\n"
            f"- Camera MUST complete full cycle and return to EXACT starting position in {duration}s\n"
            f"- Use CIRCULAR or OSCILLATING motion (orbit, zoom cycle, rotation)\n"
            f"- NO LINEAR MOTION, NO CUTS\n"
            f"- Seamless loop - last frame matches first frame\n"
            f"- Smooth, meditative pacing\n"
            f"- Crystal clear, sharp details\n"
            f"- Professional cinematography quality\n"
            f"- Generate synchronized ASMR audio"
        )
        
        # Negative prompt to avoid unwanted content
        negative_prompt = (
            "text overlays, watermarks, logos, people, faces, hands, "
            "urban scenes, cars, buildings, technology, screens, "
            "violent content, disturbing imagery, low quality, blurry, "
            "jerky motion, abrupt cuts, linear camera movement"
        )
        
        print(f"Attempting Veo 3 generation in 9:16 portrait...", flush=True)
        print(f"Target: 1080x1920, {duration}s duration", flush=True)
        
        try:
            # Use proper GenerateVideosConfig
            operation = client.models.generate_videos(
                model="veo-3.1-generate-preview",
                prompt=enhanced_prompt,
                config=types.GenerateVideosConfig(
                    aspect_ratio="9:16",
                    resolution="1080p",
                    negative_prompt=negative_prompt,
                ),
            )
            
            print(f"Operation started: {operation.name}", flush=True)
            print(f"Config: 9:16 portrait, 1080p, {duration}s with negative prompt", flush=True)
            
        except Exception as e:
            print(f"ERROR: Veo 3 generation failed: {e}", flush=True)
            
            if "403" in str(e) or "permission" in str(e).lower():
                print("REASON: API key lacks Veo 3 permissions", flush=True)
            elif "404" in str(e):
                print("REASON: Veo 3 model not found", flush=True)
            elif "quota" in str(e).lower():
                print("REASON: API quota exceeded", flush=True)
            else:
                print("FALLING BACK to text-based video", flush=True)
            
            return None
        
        # Poll for completion
        poll_count = 0
        while not operation.done and poll_count < 60:
            poll_count += 1
            print(f"[{poll_count * 10}s] Polling... ({poll_count}/60)", flush=True)
            time.sleep(10)
            operation = client.operations.get(operation)
        
        if not operation.done:
            print("ERROR: Timeout (10 minutes)", flush=True)
            return None
        
        # Download video
        print("Video generation complete! Downloading...", flush=True)
        generated_video = operation.response.generated_videos[0]
        client.files.download(file=generated_video.video)
        generated_video.video.save(output_path)
        
        # Verify video quality
        try:
            import cv2
            cap = cv2.VideoCapture(output_path)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            ret, frame = cap.read()
            if ret:
                ret2, frame2 = cap.read()
                has_motion = ret2 and not (frame == frame2).all()
                cap.release()
                
                print(f"\nVIDEO QUALITY CHECK:")
                print(f"  Resolution: {width}x{height}")
                print(f"  FPS: {fps}")
                print(f"  Frames: {frame_count}")
                print(f"  Has motion: {'YES (Real video)' if has_motion else 'NO (Static/Text slides)'}")
                
                if not has_motion:
                    print("  WARNING: This appears to be static frames, not Veo 3 video!")
                elif height <= width:
                    print(f"  WARNING: Not portrait! ({width}x{height})")
                else:
                    print("  SUCCESS: High-quality Veo 3 video confirmed!")
            else:
                cap.release()
        except Exception as e:
            print(f"Could not verify properties: {e}")
        
        print(f"SUCCESS: Video saved to {output_path}", flush=True)
        return output_path
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return None

def render_frames(captions, size=(1080, 1920), bg_color=(10, 10, 14), fg_color=(240, 240, 240)):
    """Render text frames as PIL Images (fallback if Veo 3 fails)."""
    print(f"Rendering {len(captions)} fallback frames...", flush=True)
    frames = []
    
    try:
        font = ImageFont.truetype("C:\\Windows\\Fonts\\Arial.ttf", 56)
    except:
        font = ImageFont.load_default()
    
    for text in captions:
        img = Image.new("RGB", size, color=bg_color)
        draw = ImageDraw.Draw(img)
        
        words = text.split()
        lines = []
        cur = []
        
        for w in words:
            test = " ".join(cur + [w])
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= size[0] * 0.8:
                cur.append(w)
            else:
                if cur:
                    lines.append(" ".join(cur))
                cur = [w]
        if cur:
            lines.append(" ".join(cur))
        
        y = (size[1] - len(lines) * 70) // 2
        for ln in lines:
            bbox = draw.textbbox((0, 0), ln, font=font)
            x = (size[0] - (bbox[2] - bbox[0])) // 2
            draw.text((x, y), ln, font=font, fill=fg_color)
            y += 70
        
        frames.append(img)
    
    return frames

def assemble_video(frames, output_path, total_duration=8, fps=24):
    """Assemble PIL Images into MP4 video (fallback)."""
    import numpy as np
    
    print(f"Assembling {len(frames)} frames into {total_duration}s video...", flush=True)
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    per_scene = total_duration / len(frames)
    clips = [ImageClip(np.array(f), duration=per_scene) for f in frames]
    
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(str(output_path), fps=fps, codec="libx264", audio=False)
    
    print(f"SUCCESS: Fallback video saved to {output_path}", flush=True)

def main():
    parser = argparse.ArgumentParser(description="Generate 8s ASMR video using Veo 3")
    parser.add_argument("--trends-json", required=True, help="Path to trends.json")
    parser.add_argument("--theme-file", required=True, help="Path to theme.txt")
    parser.add_argument("--output", required=True, help="Output MP4 path")
    parser.add_argument("--output-prompt", help="Save Veo 3 prompt (optional)")
    parser.add_argument("--output-narration", help="Save narration (optional)")
    parser.add_argument("--duration", type=int, default=8, help="Video duration (default: 8)")
    args = parser.parse_args()

    if not os.path.exists(args.trends_json):
        _fail(f"Trends file not found: {args.trends_json}")

    try:
        with open(args.trends_json, "r", encoding="utf-8") as f:
            trends = json.load(f)
        
        with open(args.theme_file, "r", encoding="utf-8") as f:
            theme = f.read().strip()
        
        print(f"Theme: {theme}", flush=True)
        
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            _fail("GEMINI_API_KEY not set in .env")
        
        print("\n" + "="*60)
        print("STEP 1: Generating Veo 3 prompt with Gemini")
        print("="*60 + "\n")
        
        veo3_prompt = generate_veo3_prompt_with_gemini(theme, trends, gemini_api_key)
        print(f"\nVeo 3 Prompt:\n{veo3_prompt}\n")
        
        if args.output_prompt:
            os.makedirs(os.path.dirname(os.path.abspath(args.output_prompt)), exist_ok=True)
            with open(args.output_prompt, "w", encoding="utf-8") as f:
                f.write(veo3_prompt)
        
        if args.output_narration:
            os.makedirs(os.path.dirname(os.path.abspath(args.output_narration)), exist_ok=True)
            with open(args.output_narration, "w", encoding="utf-8") as f:
                f.write(veo3_prompt)
        
        print("\n" + "="*60)
        print("STEP 2: Attempting Veo 3 video generation")
        print("="*60 + "\n")
        
        veo3_video = generate_video_with_veo3(veo3_prompt, gemini_api_key, args.duration, args.output)
        
        if not veo3_video or not os.path.exists(args.output):
            print("\n" + "="*60)
            print("VEO 3 FAILED - Using text-based fallback")
            print("="*60)
            print("\nGenerating text-based video...")
            
            captions = [theme, veo3_prompt[:200]]
            frames = render_frames(captions)
            assemble_video(frames, args.output, total_duration=args.duration, fps=24)
            print("\nFallback video created")
        else:
            print("\n" + "="*60)
            print("SUCCESS: Veo 3 video generated!")
            print("="*60)
        
        if os.path.exists(args.output):
            file_size = os.path.getsize(args.output)
            print(f"\nVideo complete! Duration: {args.duration}s, Size: {file_size:,} bytes")
        else:
            _fail("Video file not created!")
        
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
