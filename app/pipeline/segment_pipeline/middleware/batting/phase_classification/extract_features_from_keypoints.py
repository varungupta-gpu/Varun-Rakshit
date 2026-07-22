"""
Phase Classification Feature Extraction
=====================================

Extract features from keypoints for phase classification using the same
feature extraction methods as shot detection.

IMPORTANT: All speed features are normalized to 30 FPS for consistency.
- Input videos can be any FPS (25, 30, 60, etc.)
- Speed features are always calculated as if video was 30 FPS
- This ensures consistent training/testing across different video frame rates
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd

# Import extract_shot_features from local module (now in same directory)
from . import extract_shot_features


def extract_features_from_keypoints_df(keypoints_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract features from keypoints DataFrame for phase classification.
    
    This is the API-compatible function for batting pipeline integration.
    Takes DataFrame as input, returns DataFrame with features.
    
    Parameters
    ----------
    keypoints_df : pd.DataFrame
        DataFrame with batsman keypoints (COCO format)
        Required columns: frame, nose_x, nose_y, left_shoulder_x, etc.
    
    Returns
    -------
    pd.DataFrame
        DataFrame with extracted features
    """
    # Create temporary file for keypoints
    with tempfile.NamedTemporaryFile(mode='w', suffix='_keypoints.csv', delete=False) as f:
        keypoints_df.to_csv(f.name, index=False)
        temp_keypoints_path = Path(f.name)
    
    try:
        # Extract features using the existing function (without normalization)
        features_path = extract_shot_features.extract_features(
            keypoints_csv=temp_keypoints_path,
            output_csv=None  # Return temp file path
        )
        
        # Load features into DataFrame
        features_df = pd.read_csv(features_path)
        
        return features_df
    finally:
        # Clean up temporary files
        if temp_keypoints_path.exists():
            temp_keypoints_path.unlink()



