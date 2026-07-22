#!/usr/bin/env python3
"""
Test batting pipeline with dummy data
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# Add project root to path (6 levels up from tests directory)
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.pipeline.segment_pipeline.middleware.pipeline import run_pipeline_batsman
from app.pipeline.segment_pipeline.agents.batting_agent import generate_llm_analysis

# Create dummy batsman keypoints data (COCO format)
def create_dummy_batsman_keypoints(num_frames=100):
    """Create dummy batsman keypoints for testing"""
    data = []
    for frame in range(num_frames):
        row = {'frame': frame, 'frame_no': frame, 'video_id': 'test_video_123'}
        # Add COCO keypoints for batsman (full COCO format)
        keypoints = ['nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear',
                    'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
                    'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
                    'left_knee', 'right_knee', 'left_ankle', 'right_ankle']
        
        for kp in keypoints:
            # Add some variation to simulate movement
            row[f'{kp}_x'] = 100 + np.random.randn() * 10
            row[f'{kp}_y'] = 200 + np.random.randn() * 10
        
        data.append(row)
    
    return pd.DataFrame(data)

def test_batting_pipeline():
    """Test the batting pipeline with dummy data"""
    print("="*70)
    print("TESTING BATTING PIPELINE WITH DUMMY DATA")
    print("="*70)
    
    # Step 1: Create dummy keypoints
    print("\n1. Creating dummy batsman keypoints...")
    batsman_keypoints_df = create_dummy_batsman_keypoints(num_frames=100)
    print(f"   ✓ Created {len(batsman_keypoints_df)} frames")
    print(f"   ✓ Columns: {list(batsman_keypoints_df.columns[:5])}...")
    
    # Step 2: Run batting pipeline
    print("\n2. Running batting pipeline (phase prediction, biomechanics, stats)...")
    try:
        batting_report, batting_metadata = run_pipeline_batsman(batsman_keypoints_df)
        print("   ✓ Batting pipeline completed successfully")
        print(f"   ✓ Report keys: {list(batting_report.keys())}")
        print(f"   ✓ Metadata keys: {list(batting_metadata.keys())}")
    except Exception as e:
        print(f"   ✗ Batting pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Generate LLM analysis
    print("\n3. Generating LLM batting analysis...")
    try:
        output_dir = Path("output") / "test_batting_analysis"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        success = generate_llm_analysis(
            biomech_features_dict=batting_report["biomechanics_features"],
            statistics_dict=batting_report["biomechanics_statistics"],
            output_dir=output_dir
        )
        
        if success:
            print("   ✓ LLM analysis generated successfully")
            llm_json_path = output_dir / "style_analysis.json"
            if llm_json_path.exists():
                print(f"   ✓ Report saved to: {llm_json_path}")
                import json
                with open(llm_json_path, 'r') as f:
                    llm_response = json.load(f)
                print(f"   ✓ Response keys: {list(llm_response.keys())}")
            return True
        else:
            print("   ✗ LLM analysis failed")
            return False
    except Exception as e:
        print(f"   ✗ LLM analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_batting_pipeline()
    print("\n" + "="*70)
    if success:
        print("✅ BATTING PIPELINE TEST PASSED")
    else:
        print("❌ BATTING PIPELINE TEST FAILED")
    print("="*70)
    sys.exit(0 if success else 1)
