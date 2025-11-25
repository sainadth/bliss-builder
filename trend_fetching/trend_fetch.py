import os
import sys
import argparse
import re
import json
import dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
from groq import Groq

dotenv.load_dotenv()

HASHTAG_RE = re.compile(r"#([\w\d_]+)")

ASMR_KEYWORDS = [
    'asmr', 'relaxing', 'sleep', 'calm', 'soothing', 'meditation',
    'whisper', 'tingles', 'peaceful', 'ambient', 'calming', 'quiet',
    'soft spoken', 'rain sounds', 'nature sounds', 'white noise'
]

def extract_hashtags(*texts):
    """Extract unique hashtags from texts."""
    hashtags = []
    for t in texts:
        if t:
            hashtags.extend([m.group(1) for m in HASHTAG_RE.finditer(t)])
    
    seen = set()
    unique = []
    for h in hashtags:
        if h.lower() not in seen:
            seen.add(h.lower())
            unique.append(h)
    return unique

def is_asmr_related(title, description, tags, hashtags):
    """Check if video is ASMR-related."""
    combined = f"{title} {description} {' '.join(tags)} {' '.join(hashtags)}".lower()
    return any(kw in combined for kw in ASMR_KEYWORDS)

def search_asmr_videos(api_key, max_results=50):
    """Search for ASMR videos using YouTube search API."""
    youtube = build('youtube', 'v3', developerKey=api_key)
    video_ids = []
    next_page_token = None
    
    while len(video_ids) < max_results:
        try:
            request = youtube.search().list(
                part='snippet',
                q='ASMR',
                type='video',
                order='viewCount',
                maxResults=min(50, max_results - len(video_ids)),
                pageToken=next_page_token,
                relevanceLanguage='en',
                safeSearch='strict',
                videoDefinition='high',
                publishedAfter=(datetime.datetime.now() - datetime.timedelta(days=7)).isoformat() + 'Z'
            )
            response = request.execute()
            
            for item in response.get('items', []):
                video_id = item['id'].get('videoId')
                if video_id:
                    video_ids.append(video_id)
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        except HttpError as e:
            print(f"HTTP error: {e}")
            break
    
    return video_ids

def get_video_details(api_key, video_ids):
    """Get full details for videos by IDs."""
    youtube = build('youtube', 'v3', developerKey=api_key)
    videos = []
    
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i+50]
        try:
            request = youtube.videos().list(
                part='snippet,statistics',
                id=','.join(batch_ids)
            )
            videos.extend(request.execute().get('items', []))
        except HttpError as e:
            print(f"HTTP error: {e}")
    
    return videos

def collect_trends_with_metadata(youtube_api_key: str, region: str = "US", max_results: int = 50):
    """Collect ASMR trending videos with metadata."""
    print("Searching for trending ASMR videos...")
    video_ids = search_asmr_videos(youtube_api_key, max_results=max_results)
    
    if not video_ids:
        print("No ASMR videos found.")
        return []
    
    print(f"Found {len(video_ids)} videos, fetching details...")
    videos = get_video_details(youtube_api_key, video_ids)
    
    results = []
    for v in videos:
        snip = v.get('snippet', {})
        title = snip.get('title', '')
        description = snip.get('description', '')
        tags = snip.get('tags', [])
        hashtags = extract_hashtags(title, description)
        
        if is_asmr_related(title, description, tags, hashtags):
            results.append({
                "video_id": v.get('id'),
                "title": title,
                "channel": snip.get('channelTitle', ''),
                "published_at": snip.get('publishedAt'),
                "description": description,
                "hashtags": hashtags,
                "keywords": tags,
                "view_count": v.get('statistics', {}).get('viewCount', '0'),
            })
        
        if len(results) >= max_results:
            break
    
    print(f"Collected {len(results)} ASMR videos")
    return results

def extract_theme_with_llm(trends, api_key: str):
    """Use Groq LLM to extract ASMR theme from trending videos."""
    if not api_key:
        print("Warning: No GROQ_API_KEY, using fallback.", flush=True)
        return _fallback_theme_extraction(trends)
    
    try:
        import random
        
        client = Groq(api_key=api_key)
        
        # Random sample for variety
        sample_size = random.randint(10, 15)
        sampled = random.sample(trends[:20], min(sample_size, len(trends[:20])))
        
        # Build context
        context = "\n\n".join([
            f"Title: {item.get('title', '')}\n"
            f"Keywords: {', '.join((item.get('keywords') or [])[:5])}\n"
            f"Hashtags: {', '.join((item.get('hashtags') or [])[:5])}"
            for item in sampled
        ])
        
        # Random creative variations
        perspectives = ["texture-focused", "sound design", "visual aesthetics", "tactile sensation", "relaxation technique"]
        styles = ["materials and textures", "auditory experience", "visual flow", "sensory journey", "meditative quality"]
        
        prompt = (
            f"You are an ASMR content strategist analyzing trending videos from a {random.choice(perspectives)} perspective. "
            f"Based on these trending ASMR videos, create ONE unique theme (6-14 words) that {random.choice(styles)}.\n\n"
            f"Be highly creative, brand-safe, and peaceful. Use vivid sensory imagery.\n\n"
            f"{context}\n\n"
            f"Examples: 'cardboard crafting with satisfying crushing sounds', 'colorful kinetic sand cutting', "
            f"'soft spoken unboxing with crinkling paper'\n\n"
            f"Output ONLY the theme (6-14 words)."
        )
        
        print("Calling Groq API...", flush=True)
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a creative ASMR expert who creates unique, specific themes. Never repeat generic concepts."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=120,
            temperature=0.95,
            top_p=0.98,
            frequency_penalty=0.7,
            presence_penalty=0.5,
            seed=random.randint(1, 1000000)
        )
        
        theme = chat_completion.choices[0].message.content.strip().strip('"').strip("'")
        
        if theme and len(theme.split()) >= 4:
            print(f"Extracted theme: {theme}", flush=True)
            return theme
        else:
            print(f"Invalid theme, using fallback.", flush=True)
            return _fallback_theme_extraction(trends)
            
    except Exception as e:
        print(f"LLM extraction failed ({e}), using fallback.", flush=True)
        return _fallback_theme_extraction(trends)

def _fallback_theme_extraction(trends):
    """Generate random creative theme from trend titles."""
    import random
    
    if not trends:
        return "gentle rain over a peaceful forest"
    
    variations = [
        ("cardboard", "creative cardboard crafting with satisfying crushing sounds"),
        ("squishy", "colorful squishy toy cleaning with gentle squishing"),
        ("sand", "kinetic sand cutting and molding with crunchy textures"),
        ("foam", "delicate foam sculpting with airy whisper sounds"),
        ("unboxing", "soft spoken gift unboxing with crinkling paper sounds"),
        ("cooking", "peaceful cooking demonstration with sizzling and chopping"),
        ("cleaning", "satisfying deep cleaning with scrubbing and foaming"),
        ("tapping", "delicate glass tapping with crystal resonance"),
        ("whisper", "soft spoken storytelling with gentle breath sounds"),
        ("mystery", "mystery item reveals with anticipation and soft unwrapping"),
        ("paint", "slow motion paint mixing in swirling hypnotic patterns"),
        ("water", "tranquil water pouring with cascading liquid sounds")
    ]
    
    # Find trending keywords
    theme_scores = {}
    for trend in trends[:20]:
        combined = f"{trend.get('title', '')} {trend.get('description', '')}".lower()
        for keyword, _ in variations:
            if keyword in combined:
                theme_scores[keyword] = theme_scores.get(keyword, 0) + 1
    
    # Get top matches
    top_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    
    if top_themes and top_themes[0][1] > 0:
        matching = [v for k, v in variations if k in [t[0] for t in top_themes]]
        if matching:
            return random.choice(matching)
    
    return random.choice([v for _, v in variations])

def main():
    parser = argparse.ArgumentParser(description="Collect YouTube ASMR trends and extract theme")
    parser.add_argument("--output-json", required=True, help="Path to write trends JSON")
    parser.add_argument("--output-theme", help="Path to write extracted theme (optional)")
    parser.add_argument("--region", default="US", help="YouTube region code")
    parser.add_argument("--max", type=int, default=50, help="Number of videos to fetch")
    args = parser.parse_args()

    youtube_api_key = os.getenv("YOUTUBE_API_KEY")
    if not youtube_api_key:
        print("ERROR: YOUTUBE_API_KEY not set")
        sys.exit(1)

    # Fetch trends
    print("Fetching ASMR trending videos...")
    data = collect_trends_with_metadata(youtube_api_key, region=args.region, max_results=args.max)

    if not data:
        print("ERROR: No ASMR videos found")
        sys.exit(1)

    # Save trends
    os.makedirs(os.path.dirname(os.path.abspath(args.output_json)), exist_ok=True)
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"SUCCESS: Saved {len(data)} videos to {args.output_json}")
    
    # Extract theme
    if args.output_theme:
        groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not groq_api_key:
            print("WARNING: GROQ_API_KEY not set")
        
        print("\nExtracting theme...")
        theme = extract_theme_with_llm(data, groq_api_key)
        
        os.makedirs(os.path.dirname(os.path.abspath(args.output_theme)), exist_ok=True)
        with open(args.output_theme, "w", encoding="utf-8") as f:
            f.write(theme)
        
        print(f"SUCCESS: Saved theme to {args.output_theme}")
        print(f"Theme: {theme}")

if __name__ == "__main__":
    main()