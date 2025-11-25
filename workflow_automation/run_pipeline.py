import os
import sys
import logging
import subprocess
from datetime import datetime
from pathlib import Path  # ADD THIS IMPORT
import csv

# Define paths to scripts and output directory
BASE_DIR = Path(__file__).resolve().parent.parent  # Go up one level to project root
TREND_GEN_SCRIPT = BASE_DIR / "trend_fetching" / "trend_fetch.py"
VIDEO_GEN_SCRIPT = BASE_DIR / "video_generation" / "gemini_video.py"
OUTPUTS_DIR = BASE_DIR / "output"

# Ensure output directory exists
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(BASE_DIR / "pipeline_log.txt")
    ]
)

logger = logging.getLogger(__name__)  # ADD THIS LINE

def run_script(script_path, *args):
    """Run a Python script with arguments."""
    cmd = [sys.executable, str(script_path)] + list(args)
    logging.info(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        logging.error(f"Error running script {script_path}: {result.stderr}")
        raise RuntimeError(f"Script {script_path} failed with error: {result.stderr.strip()}")
    
    logging.info(f"Script {script_path} completed successfully.")
    return result.stdout.strip()

def log_pipeline_result(timestamp: str, output_dir: str, success: bool, error: str = None):
    """Log pipeline execution result to CSV."""
    log_file = os.path.join(BASE_DIR, "output", "pipeline_log.csv")
    
    # Create log file with headers if it doesn't exist
    file_exists = os.path.exists(log_file)
    
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header if new file
            if not file_exists:
                writer.writerow(['timestamp', 'success', 'output_dir', 'theme', 'video_id', 'video_url', 'error'])
            
            # Read theme and upload result if successful
            theme = "N/A"
            video_id = ""
            video_url = ""
            
            if success:
                try:
                    theme_file = os.path.join(output_dir, "theme.txt")
                    if os.path.exists(theme_file):
                        with open(theme_file, 'r', encoding='utf-8') as tf:
                            theme = tf.read().strip()
                    
                    result_file = os.path.join(output_dir, "upload_result.json")
                    if os.path.exists(result_file):
                        import json
                        with open(result_file, 'r', encoding='utf-8') as rf:
                            result = json.load(rf)
                            video_id = result.get('video_id', '')
                            video_url = result.get('video_url', '')
                except Exception as e:
                    logger.warning(f"Could not read theme/result: {e}")
            
            # Write log entry
            writer.writerow([
                timestamp,
                'true' if success else 'false',
                output_dir,
                theme,
                video_id,
                video_url,
                error or 'None'
            ])
        
        logger.info(f"Logged result to {log_file}")
        
    except Exception as e:
        logger.error(f"Failed to write log: {e}")

def run_pipeline():
    """Execute the complete Bliss Builder pipeline."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(BASE_DIR, "output", timestamp)
    
    logger.info("=== Bliss Builder Pipeline Started ===")
    logger.info(f"Starting pipeline run: {timestamp}")
    logger.info(f"Output directory: {output_dir}")
    
    try:
        # Step 1: Fetch ASMR trends and extract theme
        logger.info("Step 1: Fetching ASMR trends and extracting theme...")
        trends_json = os.path.join(output_dir, "trends.json")
        theme_file = os.path.join(output_dir, "theme.txt")
        
        run_script(
            os.path.join(BASE_DIR, "trend_fetching", "trend_fetch.py"),
            "--output-json", trends_json,
            "--output-theme", theme_file,
            "--region", "US",
            "--max", "50"
        )
        
        # Step 2: Generate video with Veo 3
        logger.info("Step 2: Generating narration and video...")
        video_file = os.path.join(output_dir, "asmr_video.mp4")
        narration_file = os.path.join(output_dir, "narration.txt")
        prompt_file = os.path.join(output_dir, "veo3_prompt.txt")
        
        run_script(
            os.path.join(BASE_DIR, "video_generation", "gemini_video.py"),
            "--trends-json", trends_json,
            "--theme-file", theme_file,
            "--output", video_file,
            "--output-narration", narration_file,
            "--output-prompt", prompt_file,
            "--duration", "8"
        )
        
        # Step 3: Upload to YouTube as PUBLIC Short with AI disclosure
        logger.info("Step 3: Uploading to YouTube as PUBLIC Short with AI disclosure...")
        upload_result_file = os.path.join(output_dir, "upload_result.json")
        
        run_script(
            os.path.join(BASE_DIR, "video_upload", "youtube_upload.py"),
            "--video", video_file,
            "--theme-file", theme_file,
            "--narration-file", narration_file,
            "--output-result", upload_result_file,
            "--privacy", "public"  # CHANGED: Set to public by default
        )
        
        # Step 4: Log results
        logger.info("Step 4: Logging pipeline results...")
        log_pipeline_result(timestamp, output_dir, success=True)
        
        logger.info("=== Bliss Builder Pipeline Completed Successfully ===")
        return True
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        log_pipeline_result(timestamp, output_dir, success=False, error=str(e))
        return False
    finally:
        logger.info("=== Bliss Builder Pipeline Finished ===")

def main():
    logger.info("=== Bliss Builder Pipeline Started ===")
    
    try:
        run_pipeline()
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
    finally:
        logger.info("=== Bliss Builder Pipeline Finished ===")

if __name__ == "__main__":
    main()