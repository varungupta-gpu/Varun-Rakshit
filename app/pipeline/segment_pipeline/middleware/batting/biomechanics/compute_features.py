"""
Compute biomechanical features for each inferred batting phase.

In-memory API functions:
- compute_batting_features() - API-compatible function for pipeline integration
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Import local features module
from . import features


# Feature → phase mapping (from biomechanics field/phase table)
PHASE_FEATURES: dict[str, list[str]] = {
    "stance": [
        "hip_direction",
        "hip_shoulder_alignment",
        "head_position_stability",
        "front_knee_angle",
        "back_knee_angle",
        "stride_width",
        "front_foot_ankle_knee_line",
        "back_foot_ankle_knee_line",
        "weighted_com",
    ],
    "preparation": [
        "hip_direction",
        "hip_shoulder_alignment",
        "head_position_stability",
        "front_knee_angle",
        "back_knee_angle",
        "stride_width",
        "trunk_lateral_flexion",
        "shoulder_elbow_arm_line_dominant",
        "shoulder_elbow_arm_line_non_dominant",
        "elbow_wrist_arm_line_dominant",
        "elbow_wrist_arm_line_non_dominant",
        "front_foot_ankle_knee_line",
        "back_foot_ankle_knee_line",
        "front_foot_progression",
        "back_foot_progression",
        "stride_line_progression_angle",
        "shoulder_line_progression_angle",
        "weighted_com",
        "upper_body_rotation",
        "lower_body_rotation",
    ],
    "downswing": [
        "hip_direction",
        "hip_shoulder_alignment",
        "head_position_stability",
        "front_knee_angle",
        "back_knee_angle",
        "stride_width",
        "trunk_lateral_flexion",
        "shoulder_elbow_arm_line_dominant",
        "shoulder_elbow_arm_line_non_dominant",
        "elbow_wrist_arm_line_dominant",
        "elbow_wrist_arm_line_non_dominant",
        "front_foot_ankle_knee_line",
        "back_foot_ankle_knee_line",
        "front_foot_progression",
        "back_foot_progression",
        "stride_line_progression_angle",
        "shoulder_line_progression_angle",
        "weighted_com",
        "upper_body_rotation",
        "lower_body_rotation",
    ],
    "followthrough": [
        "hip_direction",
        "hip_shoulder_alignment",
        "head_position_stability",
        "front_knee_angle",
        "back_knee_angle",
        "stride_width",
        "trunk_lateral_flexion",
        "shoulder_elbow_arm_line_dominant",
        "shoulder_elbow_arm_line_non_dominant",
        "elbow_wrist_arm_line_dominant",
        "elbow_wrist_arm_line_non_dominant",
        "front_foot_ankle_knee_line",
        "back_foot_ankle_knee_line",
        "stride_line_progression_angle",
        "shoulder_line_progression_angle",
        "weighted_com",
        "upper_body_rotation",
        "lower_body_rotation",
    ],
}

FEATURE_FUNCTIONS = {
    "hip_direction": features.compute_hip_direction,
    "hip_shoulder_alignment": features.compute_hip_shoulder_alignment,
    "shoulder_tilt_progression": features.compute_shoulder_tilt_progression,
    "shoulder_tilt": features.compute_shoulder_tilt,
    "head_position_stability": features.compute_head_stability,
    "front_knee_angle": features.compute_front_knee_angle,
    "back_knee_angle": features.compute_back_knee_angle,
    "stride_width": features.compute_stride_width,
    "trunk_lateral_flexion": features.compute_trunk_lateral_flexion,
    "shoulder_elbow_arm_line_dominant": features.compute_dominant_shoulder_elbow_line,
    "shoulder_elbow_arm_line_non_dominant": features.compute_nondominant_shoulder_elbow_line,
    "elbow_wrist_arm_line_dominant": features.compute_dominant_elbow_wrist_line,
    "elbow_wrist_arm_line_non_dominant": features.compute_nondominant_elbow_wrist_line,
    "front_foot_ankle_knee_line": features.compute_front_foot_ankle_knee_line,
    "back_foot_ankle_knee_line": features.compute_back_foot_ankle_knee_line,
    "front_foot_progression": features.compute_front_foot_progression,
    "back_foot_progression": features.compute_back_foot_progression,
    "stride_line_progression_angle": features.compute_stride_line_progression_angle,
    "shoulder_line_progression_angle": features.compute_shoulder_line_progression_angle,
    "weighted_com": features.compute_weighted_com,
    "upper_body_rotation": features.compute_upper_body_rotation,
    "lower_body_rotation": features.compute_lower_body_rotation,
}

STANCE_DEPENDENT_FEATURES = {
    "head_position_stability",
    "trunk_lateral_flexion",
    "front_foot_progression",
    "back_foot_progression",
    "stride_line_progression_angle",
    "shoulder_line_progression_angle",
    "weighted_com",
    "upper_body_rotation",
    "lower_body_rotation",
}


def compute_batting_features(
    phases_df: pd.DataFrame,
    keypoints_df: pd.DataFrame
) -> dict:
    """
    IN-MEMORY biomechanical features computation - NO FILE I/O.
    
    This is the API-compatible function for batting pipeline integration.
    Takes DataFrames as input, returns features dict directly.
    Computes only phase-specific biomechanical features as defined in PHASE_FEATURES.
    
    Parameters
    ----------
    phases_df : pd.DataFrame
        DataFrame with batting phases
        Required columns: phase, start_frame, end_frame
    keypoints_df : pd.DataFrame
        DataFrame with batsman keypoints (COCO format)
        Required columns: frame, nose_x, nose_y, left_shoulder_x, etc.
    
    Returns
    -------
    dict
        Dictionary with features per phase:
        {phase_name: {frame_no: {feature: value, ...}}}
    
    Example
    -------
    >>> phases_df = infer_phases_from_downswing(...)
    >>> features = compute_batting_features(phases_df, keypoints_df)
    >>> features['downswing'][68]  # Features at frame 68 in downswing
    {'hip_direction': 45.2, 'shoulder_tilt': 12.3, ...}
    """
    
    if phases_df is None or phases_df.empty:
        logger.warning("phases_df is empty, returning empty features")
        return {}
    
    if keypoints_df is None or keypoints_df.empty:
        logger.warning("keypoints_df is empty, returning empty features")
        return {}
    
    features_dict = {}
    
    # Get stance frames for stance-dependent features
    stance_row = phases_df[phases_df['phase'] == 'stance']
    if stance_row.empty:
        logger.warning("No stance phase found, stance-dependent features may not work correctly")
        stance_start_frame = None
        stance_end_frame = None
    else:
        stance_start_frame = int(stance_row.iloc[0]['start_frame'])
        stance_end_frame = int(stance_row.iloc[0]['end_frame'])
    
    try:
        # Process each phase
        for _, phase_row in phases_df.iterrows():
            phase_name = phase_row.get('phase')
            start_frame = int(phase_row.get('start_frame'))
            end_frame = int(phase_row.get('end_frame'))
            
            if phase_name is None or start_frame is None or end_frame is None:
                continue
            
            # Get features specific to this phase
            phase_feature_list = PHASE_FEATURES.get(phase_name, [])
            if not phase_feature_list:
                logger.warning(f"No features defined for phase '{phase_name}'")
                continue
            
            # Compute features for this phase
            try:
                phase_features_dict = {}
                
                # Get frames in this phase
                phase_df = keypoints_df[(keypoints_df["frame"] >= start_frame) & 
                                       (keypoints_df["frame"] <= end_frame)].copy()
                
                if len(phase_df) == 0:
                    logger.warning(f"No keypoints found for phase '{phase_name}' frames {start_frame}-{end_frame}")
                    continue
                
                # Compute each feature for this phase
                for feature_name in phase_feature_list:
                    func = FEATURE_FUNCTIONS.get(feature_name)
                    if func is None:
                        logger.warning(f"Feature function not found: {feature_name}")
                        continue
                    
                    try:
                        # Call feature function with appropriate parameters
                        if feature_name in STANCE_DEPENDENT_FEATURES:
                            values = func(keypoints_df, start_frame, end_frame, stance_start_frame, stance_end_frame)
                        else:
                            values = func(keypoints_df, start_frame, end_frame)
                        
                        # Assign values to each frame in the phase
                        if isinstance(values, (pd.Series, np.ndarray)):
                            values_arr = np.asarray(values, dtype=float)
                            for idx, frame_row in phase_df.iterrows():
                                frame_no = int(frame_row['frame'])
                                if frame_no not in phase_features_dict:
                                    phase_features_dict[frame_no] = {}
                                
                                # Map array index to frame
                                frame_idx = idx - phase_df.index[0]
                                if frame_idx < len(values_arr):
                                    phase_features_dict[frame_no][feature_name] = float(values_arr[frame_idx])
                        else:
                            # Single value - assign to all frames
                            for frame_no in phase_df['frame'].values:
                                if frame_no not in phase_features_dict:
                                    phase_features_dict[frame_no] = {}
                                phase_features_dict[frame_no][feature_name] = float(values)
                                
                    except Exception as feature_error:
                        logger.error(f"Error computing feature '{feature_name}' for phase '{phase_name}': {feature_error}")
                        continue
                
                # Filter out NaN values
                for frame_no in phase_features_dict:
                    phase_features_dict[frame_no] = {
                        k: v for k, v in phase_features_dict[frame_no].items() 
                        if pd.notna(v)
                    }
                
                features_dict[phase_name] = phase_features_dict
                logger.info(f"✅ Computed features for phase '{phase_name}': {len(phase_features_dict)} frames, {len(phase_feature_list)} features")
                
            except Exception as phase_error:
                logger.error(f"Error computing features for phase {phase_name}: {phase_error}")
                continue
        
        logger.info(f"✅ Biomechanical features computed for {len(features_dict)} phases")
        return features_dict
        
    except Exception as e:
        logger.exception(f"Error computing batting features: {e}")
        return {}
