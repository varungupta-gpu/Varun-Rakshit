import json
import os
import glob
import subprocess
import sys
import uuid
from pathlib import Path

# Set static configurations
API_URL = "https://video-insights-api-988584008199.asia-south1.run.app"
GCLOUD_JOB_NAME = "analysis-processor"
GCLOUD_REGION = "asia-south1"
GCLOUD_PROJECT = "video-backend-dev"

def load_video_data(path="*.json"):
    """Reads all .json files matching the pattern and extracts video data."""
    # Try the path as given (relative to CWD)
    json_files = glob.glob(path)
    
    # If no files found and not an absolute path, try relative to script directory
    if not json_files and not os.path.isabs(path):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        json_files = glob.glob(os.path.join(script_dir, path))
    
    print(f"Found {len(json_files)} matching file(s): {json_files}")
    
    all_video_data = []
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_video_data.extend(data)
                elif isinstance(data, dict):
                    all_video_data.append(data)
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
            
    return all_video_data

def trigger_cloud_job(payload):
    """Triggers a Cloud Run job for a single segment analysis."""
    payload_str = json.dumps(payload)
    
    cmd = [
        "gcloud", "run", "jobs", "execute", GCLOUD_JOB_NAME,
        f"--region={GCLOUD_REGION}",
        f"--project={GCLOUD_PROJECT}",
        f"--args={payload_str}"
    ]
    
    print(f"  Executing command: {' '.join(cmd[:4])} ...")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"  Successfully triggered job for segment: {payload.get('segment_id')}")
    except subprocess.CalledProcessError as e:
        print(f"  Error triggering job for segment {payload.get('segment_id')}: {e}")

def run_processing_on_videos(video_data):
    """Processes segments for each video by triggering Cloud Run jobs."""
    for vid in video_data:
        video_id = vid.get('video_id')
        if not video_id: 
            continue
            
        segments = vid.get('segments', [])
        print(f"\n--- Processing Video ID: {video_id} ({len(segments)} segments) ---")
        
        for segment_entry in segments:
            # Handle both string (old) and object (new) format for compatibility
            if isinstance(segment_entry, str):
                s_id = segment_entry
                si_id = segment_entry
            else:
                s_id = segment_entry.get("segment_id", "")
                si_id = segment_entry.get("segment_insight_id", s_id)

            print(f"-> Triggering analysis for segment: {s_id}")
            
            # Construct the payload for the analysis job
            payload = {
                "request_id": str(uuid.uuid4()),
                "video_id": video_id,
                "llm_insight_id": vid.get("llm_insight_id", ""),  
                "segment_id": s_id,
                "segment_insight_id": si_id,
                "api_base_url": API_URL,
                "bearer_access_token": vid.get("token", "")
            }
            
            trigger_cloud_job(payload)
            
if __name__ == "__main__":
    # If a path argument is provided, use it, otherwise fallback to default
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
    else:
        target_path = "demo_data.json"

    print(f"Loading data from: {target_path}")
    video_data = load_video_data(target_path)
    
    if not video_data:
        print("No video data found in JSON files.")
    else:
        print(f"Loaded {len(video_data)} video entries.")
        run_processing_on_videos(video_data)
