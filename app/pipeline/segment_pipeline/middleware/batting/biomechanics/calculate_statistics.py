#!/usr/bin/env python3
"""
Calculate phase-wise biomechanical statistics from feature CSV.
Generates JSON 1 format as specified in TEMP.md

In-memory API functions:
- calculate_phase_statistics() - API-compatible function for pipeline integration
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def calculate_phase_stats(phase_df, features):
    """Calculate statistics for all features in a phase"""
    stats = {}
    
    for feature in features:
        if feature not in phase_df.columns:
            continue
        
        values = phase_df[feature].dropna()
        if len(values) == 0:
            continue
        
        feature_stats = {}
        
        # Basic statistics
        feature_stats['mean'] = float(values.mean())
        feature_stats['signed_mean'] = float(values.mean())  # Same as mean
        feature_stats['median'] = float(values.median())
        feature_stats['std'] = float(values.std())
        feature_stats['variance'] = float(values.var())
        
        # Min/Max/Range
        feature_stats['min'] = float(values.min())
        feature_stats['max'] = float(values.max())
        feature_stats['range'] = float(values.max() - values.min())
        
        # Percentiles
        feature_stats['p5'] = float(values.quantile(0.05))
        feature_stats['p95'] = float(values.quantile(0.95))
        
        # Delta (last - first)
        if len(values) > 1:
            feature_stats['delta'] = float(values.iloc[-1] - values.iloc[0])
        
        stats[feature] = feature_stats
    
    return stats


def calculate_biomech_statistics(csv_path, output_path=None):
    """
    Calculate phase-wise biomechanical statistics from CSV.
    
    Args:
        csv_path: Path to biomechanics features CSV
        output_path: Path to save JSON output (optional)
    
    Returns:
        Dictionary with phase-wise statistics
    """
    df = pd.read_csv(csv_path)
    
    # Define features per phase based on TEMP.md
    stance_features = [
        'hip_direction',
        'shoulder_line_progression_angle',
        'stride_line_progression_angle',
        'hip_shoulder_alignment',
        'front_foot_ankle_knee_line',
        'back_foot_ankle_knee_line',
        'stride_width'
    ]
    
    preparation_features = [
        'front_foot_progression',
        'back_foot_progression',
        'weighted_com',
        'hip_direction',
        'shoulder_line_progression_angle',
        'trunk_lateral_flexion',
        'upper_body_rotation',
        'lower_body_rotation',
        'hip_shoulder_alignment',
        'front_knee_angle',
        'back_knee_angle',
        'stride_line_progression_angle'
    ]
    
    downswing_features = [
        'upper_body_rotation',
        'lower_body_rotation',
        'weighted_com',
        'front_foot_progression',
        'back_foot_progression',
        'trunk_lateral_flexion',
        'front_knee_angle',
        'back_knee_angle',
        'shoulder_elbow_arm_line_dominant',
        'shoulder_elbow_arm_line_non_dominant',
        'hip_direction',
        'shoulder_line_progression_angle'
    ]
    
    followthrough_features = [
        'head_position_stability',
        'weighted_com',
        'trunk_lateral_flexion',
        'upper_body_rotation',
        'lower_body_rotation',
        'front_knee_angle',
        'back_knee_angle',
        'shoulder_elbow_arm_line_dominant',
        'shoulder_elbow_arm_line_non_dominant',
        'hip_direction',
        'shoulder_line_progression_angle',
        'hip_shoulder_alignment'
    ]
    
    head_position_features = [
        'head_position_stability',
        'trunk_lateral_flexion',
        'weighted_com',
        'hip_shoulder_alignment'
    ]
    
    # Calculate statistics per phase
    result = {}
    
    # Stance
    stance_df = df[df['phase'] == 'stance']
    if len(stance_df) > 0:
        result['stance'] = calculate_phase_stats(stance_df, stance_features)
    
    # Preparation
    prep_df = df[df['phase'] == 'preparation']
    if len(prep_df) > 0:
        result['preparation'] = calculate_phase_stats(prep_df, preparation_features)
    
    # Downswing
    down_df = df[df['phase'] == 'downswing']
    if len(down_df) > 0:
        result['downswing'] = calculate_phase_stats(down_df, downswing_features)
    
    # Follow-through
    follow_df = df[df['phase'] == 'followthrough']
    if len(follow_df) > 0:
        result['followthrough'] = calculate_phase_stats(follow_df, followthrough_features)
    
    # Head position (aggregate across all phases)
    result['head_position'] = calculate_phase_stats(df, head_position_features)
    
    # Save to file if output path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"[OK] Saved statistics to: {output_path}")
    
    return result


def calculate_phase_statistics(features_dict: dict) -> dict:
    """
    IN-MEMORY statistics calculation - NO FILE I/O.
    
    This is the API-compatible function for batting pipeline integration.
    Takes features dict as input, returns statistics dict directly.
    
    Parameters
    ----------
    features_dict : dict
        Dictionary with biomechanical features per phase
        Format: {phase_name: {frame_no: {feature: value, ...}}}
    
    Returns
    -------
    dict
        Dictionary with phase-wise statistics:
        {phase_name: {feature: {mean, std, min, max, ...}}}
    
    Example
    -------
    >>> features_dict = {...}  # From compute_batting_features()
    >>> stats = calculate_phase_statistics(features_dict)
    >>> print(stats['downswing']['hip_direction']['mean'])
    42.5
    """
    
    if not features_dict:
        return {}
    
    # Define features per phase
    stance_features = [
        'hip_direction', 'shoulder_line_progression_angle',
        'stride_line_progression_angle', 'hip_shoulder_alignment',
        'front_foot_ankle_knee_line', 'back_foot_ankle_knee_line',
        'stride_width'
    ]
    
    preparation_features = [
        'front_foot_progression', 'back_foot_progression',
        'weighted_com', 'hip_direction', 'shoulder_line_progression_angle',
        'trunk_lateral_flexion', 'upper_body_rotation', 'lower_body_rotation',
        'hip_shoulder_alignment', 'front_knee_angle', 'back_knee_angle',
        'stride_line_progression_angle'
    ]
    
    downswing_features = [
        'upper_body_rotation', 'lower_body_rotation', 'weighted_com',
        'front_foot_progression', 'back_foot_progression',
        'trunk_lateral_flexion', 'front_knee_angle', 'back_knee_angle',
        'shoulder_elbow_arm_line_dominant', 'shoulder_elbow_arm_line_non_dominant',
        'hip_direction', 'shoulder_line_progression_angle'
    ]
    
    followthrough_features = [
        'head_position_stability', 'weighted_com', 'trunk_lateral_flexion',
        'upper_body_rotation', 'lower_body_rotation', 'front_knee_angle',
        'back_knee_angle', 'shoulder_elbow_arm_line_dominant',
        'shoulder_elbow_arm_line_non_dominant', 'hip_direction',
        'shoulder_line_progression_angle', 'hip_shoulder_alignment'
    ]
    
    result = {}
    
    # Calculate statistics for each phase
    for phase_name in ['stance', 'preparation', 'downswing', 'followthrough']:
        if phase_name not in features_dict:
            continue
        
        phase_features = features_dict[phase_name]
        
        # Select appropriate feature list
        if phase_name == 'stance':
            features_to_use = stance_features
        elif phase_name == 'preparation':
            features_to_use = preparation_features
        elif phase_name == 'downswing':
            features_to_use = downswing_features
        else:  # followthrough
            features_to_use = followthrough_features
        
        # Convert phase features to DataFrame for easier calculation
        frame_data = []
        for frame_no, frame_features in phase_features.items():
            frame_row = {'frame': frame_no}
            frame_row.update(frame_features)
            frame_data.append(frame_row)
        
        if not frame_data:
            continue
        
        phase_df = pd.DataFrame(frame_data)
        
        # Calculate stats for this phase
        phase_stats = {}
        for feature in features_to_use:
            if feature not in phase_df.columns:
                continue
            
            values = phase_df[feature].dropna()
            if len(values) == 0:
                continue
            
            feature_stats = {
                'mean': float(values.mean()),
                'median': float(values.median()),
                'std': float(values.std()),
                'min': float(values.min()),
                'max': float(values.max()),
                'range': float(values.max() - values.min()),
                'count': int(len(values))
            }
            
            if len(values) > 1:
                feature_stats['delta'] = float(values.iloc[-1] - values.iloc[0])
            
            phase_stats[feature] = feature_stats
        
        result[phase_name] = phase_stats
    
    logger.info(f"✅ Statistics calculated for {len(result)} phases")
    return result
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python calculate_statistics.py <csv_path> [output_json_path]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    calculate_biomech_statistics(csv_path, output_path)
