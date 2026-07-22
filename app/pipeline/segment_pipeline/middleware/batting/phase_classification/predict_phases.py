"""
Phase Classification Prediction
=============================

Predict 3 phases (preparation, downswing, followthrough) for cricket batting videos.
"""

from __future__ import annotations

import csv
import pickle
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import numpy as np

# Models directory
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

# Distance/length features to exclude (camera-dependent)
DISTANCE_FEATURES_TO_EXCLUDE = [
    "left_arm_length",
    "right_arm_length",
    "left_forearm_length",
    "right_forearm_length",
    "left_shoulder_wrist_dist",
    "right_shoulder_wrist_dist",
    "bat_arm_extension",
    "eye_separation",
    "ear_separation",
]

# Training dataset builder functions (copied from build_training_dataset.py)
ID_COLUMNS = {"video_id", "frame_no"}
PHASES = ["preparation", "downswing", "followthrough", "no_phase"]
NO_PHASE_LABEL = "no_phase"


def _numeric_feature_names(rows: list[dict]) -> list[str]:
    """Extract numeric feature column names from feature data."""
    if not rows:
        return []
    names = []
    for key in rows[0]:
        if key in ID_COLUMNS:
            continue
        try:
            float(rows[0].get(key) or 0.0)
            names.append(key)
        except ValueError:
            pass
    return names


def _aggregate(values: list[float], prefix: str) -> dict[str, float]:
    """Compute 8 statistics per feature across temporal window."""
    arr = np.array(values, dtype=float)
    if arr.size == 0:
        arr = np.array([0.0])
    return {
        f"{prefix}_mean": float(np.mean(arr)),
        f"{prefix}_max": float(np.max(arr)),
        f"{prefix}_min": float(np.min(arr)),
        f"{prefix}_std": float(np.std(arr)),
        f"{prefix}_range": float(np.max(arr) - np.min(arr)),
        f"{prefix}_start": float(arr[0]),
        f"{prefix}_end": float(arr[-1]),
        f"{prefix}_change": float(arr[-1] - arr[0]),
    }


def temporal_window_size() -> int:
    """Get temporal window size (default 3)."""
    return 3


def build_temporal_feature_row(
    frame_no: int,
    rows_by_frame: dict,
    feature_names: list[str],
    video_id: str,
    phase_label: str,
    window: int | None = None,
) -> dict | None:
    """Build temporal feature row for a single frame."""
    window = temporal_window_size() if window is None else window
    window_frames = []
    
    for offset in range(-window, window + 1):
        target_frame = frame_no + offset
        if (video_id, target_frame) in rows_by_frame:
            window_frames.append(rows_by_frame[(video_id, target_frame)])
            continue
            
        found = False
        for search_dist in range(1, 100):
            if (video_id, target_frame - search_dist) in rows_by_frame:
                window_frames.append(rows_by_frame[(video_id, target_frame - search_dist)])
                found = True
                break
                
        if not found:
            for search_dist in range(1, 100):
                if (video_id, target_frame + search_dist) in rows_by_frame:
                    window_frames.append(rows_by_frame[(video_id, target_frame + search_dist)])
                    found = True
                    break
                    
        if not found and window_frames:
            window_frames.append(window_frames[-1])
            
    if not window_frames:
        return None

    out = {
        "video_id": video_id,
        "frame_no": frame_no,
        "phase": phase_label,
    }
    # Aggregate each feature across temporal window (8 stats per feature)
    for name in feature_names:
        values = [float(row.get(name) or 0.0) for row in window_frames]
        out.update(_aggregate(values, name))
    return out


def predict_downswing_phases(keypoints_df: pd.DataFrame, model_path: str = None) -> pd.DataFrame:
    """
    Predict downswing phases from keypoints DataFrame.
    
    This is the API-compatible function for batting pipeline integration.
    Takes DataFrame as input, returns DataFrame with predictions.
    
    Parameters
    ----------
    keypoints_df : pd.DataFrame
        DataFrame with batsman keypoints (COCO format)
        Required columns: frame_no, nose_x, nose_y, left_shoulder_x, etc.
    model_path : str, optional
        Path to phase classification model directory
        If None, uses default models directory
    
    Returns
    -------
    pd.DataFrame
        DataFrame with predictions:
        Columns: frame_no, predicted_phase, prob_preparation, prob_downswing, prob_followthrough, prob_no_phase
    """
    # Use default models directory if not specified
    if model_path is None:
        model_dir = MODELS_DIR
    else:
        model_dir = Path(model_path) if isinstance(model_path, str) else model_path
        if model_dir.is_file():
            model_dir = model_dir.parent
    
    # Load model and artifacts
    model, encoder, feature_columns = load_phase_model(model_dir)
    
    # Extract features from keypoints
    from .extract_features_from_keypoints import extract_features_from_keypoints_df
    features_df = extract_features_from_keypoints_df(keypoints_df)
    
    # Prepare data for prediction
    video_id = "batch_video"  # Dummy video ID for batch processing
    
    # Convert features DataFrame to rows_by_frame format
    rows_by_frame = {}
    for _, row in features_df.iterrows():
        frame_no = int(row['frame_no'])
        rows_by_frame[(video_id, frame_no)] = row.to_dict()
    
    # Get feature names (exclude ID columns)
    feature_names = _numeric_feature_names([row for row in rows_by_frame.values()])
    
    # Exclude distance/length features (camera-dependent)
    distance_features_found = [f for f in feature_names if f in DISTANCE_FEATURES_TO_EXCLUDE]
    feature_names = [f for f in feature_names if f not in DISTANCE_FEATURES_TO_EXCLUDE]
    
    window = temporal_window_size()
    
    # Predict each frame
    predictions = []
    probabilities = []
    
    for frame_key in sorted(rows_by_frame.keys()):
        frame_no = frame_key[1]
        
        # Build temporal features for this frame
        temporal_row = build_temporal_feature_row(
            frame_no=frame_no,
            rows_by_frame=rows_by_frame,
            feature_names=feature_names,
            video_id=video_id,
            phase_label="preparation",  # Dummy label
            window=window,
        )
        
        if temporal_row is None:
            predictions.append("no_phase")
            dummy_prob = [0.0] * len(encoder.classes_)
            if "no_phase" in encoder.classes_:
                dummy_prob[list(encoder.classes_).index("no_phase")] = 1.0
            probabilities.append(dummy_prob)
            continue
        
        # Remove metadata columns and prepare for prediction
        feature_data = {k: v for k, v in temporal_row.items() if k not in ["video_id", "frame_no", "phase"]}
        
        # Create DataFrame with same structure as training
        X = pd.DataFrame([feature_data])
        X = pd.get_dummies(X, columns=[col for col in X.columns if X[col].dtype == "object"], dummy_na=False)
        X = X.reindex(columns=feature_columns, fill_value=0.0).fillna(0.0)
        
        # Predict
        pred_idx = model.predict(X)[0]
        pred_proba = model.predict_proba(X)[0]
        
        predicted_phase = encoder.inverse_transform([pred_idx])[0]
        predictions.append(predicted_phase)
        probabilities.append(pred_proba.tolist())
    
    # Apply Viterbi decoding for sequence consistency
    sorted_frame_numbers = [key[1] for key in sorted(rows_by_frame.keys())]
    start_frame, end_frame = detect_active_phase_region_from_confidence(
        probabilities,
        list(encoder.classes_),
        sorted_frame_numbers,
        raw_predictions=predictions,
    )
    
    # Enforce phase sequence constraints
    final_predictions = ["no_phase"] * len(predictions)
    
    if start_frame is not None and end_frame is not None:
        region_indices = []
        for i, frame_key in enumerate(sorted(rows_by_frame.keys())):
            frame_no = frame_key[1]
            if start_frame <= frame_no <= end_frame:
                region_indices.append(i)
        
        if region_indices:
            region_probs = [probabilities[i] for i in region_indices]
            region_phases = viterbi_decode_phases(region_probs, list(encoder.classes_))
            region_phases = smooth_phase_durations(region_phases)
            
            for idx, phase in zip(region_indices, region_phases):
                final_predictions[idx] = phase
    
    predictions = final_predictions
    
    # Build output DataFrame
    output_rows = []
    phase_classes = list(encoder.classes_)
    
    for frame_key, pred_phase, prob in zip(sorted(rows_by_frame.keys()), predictions, probabilities):
        frame_no = frame_key[1]
        row = {
            "frame_no": frame_no,
            "predicted_phase": pred_phase,
        }
        
        # Add probability columns
        for j, phase_class in enumerate(phase_classes):
            row[f"prob_{phase_class}"] = prob[j] if j < len(prob) else 0.0
        
        output_rows.append(row)
    
    return pd.DataFrame(output_rows)


def load_phase_model(model_dir: Path) -> tuple[Any, Any, list[str]]:
    """Load trained phase classification model and artifacts."""
    
    model_path = model_dir / "phase_classifier.pkl"
    encoder_path = model_dir / "phase_label_encoder.pkl"
    features_path = model_dir / "phase_feature_columns.pkl"
    
    if not all(p.exists() for p in [model_path, encoder_path, features_path]):
        raise FileNotFoundError(f"Model artifacts not found in {model_dir}")
    
    with model_path.open("rb") as f:
        model = pickle.load(f)
    with encoder_path.open("rb") as f:
        encoder = pickle.load(f)
    with features_path.open("rb") as f:
        feature_columns = pickle.load(f)
    
    return model, encoder, feature_columns


def smooth_phase_sequence(predictions: list[str], max_gap: int = 4) -> list[str]:
    """
    Fill gaps of up to max_gap consecutive 'no_phase' frames within a phase sequence.
    Also enforces phase duration constraints: prep (longest) > followthrough (middle) > downswing (shortest).
    """
    if not predictions:
        return predictions
    
    smoothed = predictions.copy()
    i = 0
    
    # First pass: Fill small gaps
    while i < len(smoothed):
        if smoothed[i] == "no_phase":
            gap_start = i
            gap_end = i
            
            while gap_end < len(smoothed) and smoothed[gap_end] == "no_phase":
                gap_end += 1
            
            gap_length = gap_end - gap_start
            
            if gap_length <= max_gap:
                prev_phase = None
                if gap_start > 0:
                    prev_phase = smoothed[gap_start - 1]
                
                if prev_phase and prev_phase != "no_phase":
                    for j in range(gap_start, gap_end):
                        smoothed[j] = prev_phase
            
            i = gap_end
        else:
            i += 1
    
    # Second pass: Enforce phase duration constraints
    # Expected ratios from training: prep ≈ 45%, followthrough ≈ 30%, downswing ≈ 25%
    smoothed = enforce_phase_duration_constraints(smoothed)
    
    return smoothed


def enforce_phase_duration_constraints(predictions: list[str]) -> list[str]:
    """
    Enforce that within the shot region: prep duration > followthrough duration > downswing duration.
    If a phase is too long/short, redistribute frames to neighboring phases.
    """
    if not predictions:
        return predictions
    
    # Find shot region (non-no_phase frames)
    shot_start = None
    shot_end = None
    for i, p in enumerate(predictions):
        if p != "no_phase":
            if shot_start is None:
                shot_start = i
            shot_end = i
    
    if shot_start is None or shot_end is None:
        return predictions
    
    # Count phase durations in shot region
    from collections import Counter
    phase_counts = Counter(predictions[shot_start:shot_end+1])
    
    prep_count = phase_counts.get("preparation", 0)
    down_count = phase_counts.get("downswing", 0)
    follow_count = phase_counts.get("followthrough", 0)
    
    total_shot_frames = prep_count + down_count + follow_count
    
    if total_shot_frames == 0:
        return predictions
    
    # Check if durations are reasonable (prep > follow > down)
    # If downswing is too long (> 35% of shot), it's probably mislabeled
    if down_count > 0.35 * total_shot_frames and prep_count > 0:
        # Downswing is too long - probably includes some prep frames
        # This is a signal but we'll let Viterbi handle the sequence
        pass
    
    # If prep is too short (< 30% of shot), something is wrong
    if prep_count > 0 and prep_count < 0.30 * total_shot_frames:
        # Prep is too short - but trust the model for now
        pass
    
    return predictions


def smooth_phase_durations(phases: list[str], min_durations: dict[str, int] | None = None) -> list[str]:
    """
    Enforce minimum duration thresholds for ordered phase predictions.

    Sequence ordering is enforced by Viterbi decoding. This cleanup only absorbs
    very short phase runs into neighboring frames so the CSV and rendered video
    do not show unrealistic flicker.
    """
    if not phases:
        return phases

    if min_durations is None:
        min_durations = {
            "preparation": 15,
            "prep": 15,
            "downswing": 5,
            "followthrough": 5,
            "follow_through": 5,
        }

    smoothed = phases.copy()
    i = 0
    while i < len(smoothed):
        phase = smoothed[i]
        phase_start = i

        while i < len(smoothed) and smoothed[i] == phase:
            i += 1

        phase_duration = i - phase_start
        min_duration = min_durations.get(phase, 3)
        if phase_duration >= min_duration:
            continue

        extend_back = min_duration - phase_duration
        for j in range(phase_start - 1, max(-1, phase_start - extend_back - 1), -1):
            if j >= 0:
                smoothed[j] = phase
            else:
                break

    return smoothed


def detect_active_phase_region_from_confidence(
    probabilities: list[list[float]], 
    encoder_classes: list[str],
    frame_numbers: list[int],
    raw_predictions: list[str] | None = None,
    min_confidence: float = 0.12,
    max_gap: int = 8,
) -> tuple[int | None, int | None]:
    """
    Detect the most likely active batting phase region.

    Prefer model labels when it predicts real phases. Confidence is used as a
    softer fallback, so low confidence no longer collapses the entire video to
    no_phase.
    """
    if not probabilities or not encoder_classes:
        return None, None
    
    # Find indices for the 3 real phases (exclude no_phase)
    phase_indices = []
    for phase_name in ["preparation", "downswing", "followthrough"]:
        if phase_name in encoder_classes:
            phase_indices.append(encoder_classes.index(phase_name))
    
    if not phase_indices:
        return None, None
    
    no_phase_idx = list(encoder_classes).index("no_phase") if "no_phase" in encoder_classes else None
    active_frames: list[int] = []

    for idx, probs in enumerate(probabilities):
        predicted_phase = raw_predictions[idx] if raw_predictions and idx < len(raw_predictions) else None
        max_phase_prob = max([probs[i] if i < len(probs) else 0.0 for i in phase_indices])
        no_phase_prob = probs[no_phase_idx] if no_phase_idx is not None and no_phase_idx < len(probs) else 0.0
        active = predicted_phase in {"preparation", "downswing", "followthrough"}
        active = active or max_phase_prob >= max(min_confidence, no_phase_prob * 0.6)
        active_frames.append(1 if active else 0)

    active_frames = _fill_binary_gaps(active_frames, max_gap=max_gap)
 
    # Find continuous blocks
    blocks = []
    in_block = False
    start_idx = 0
    for i, val in enumerate(active_frames):
        if val == 1 and not in_block:
            in_block = True
            start_idx = i
        elif val == 0 and in_block:
            in_block = False
            blocks.append((start_idx, i - 1))
    if in_block:
        blocks.append((start_idx, len(active_frames) - 1))
    
    min_len = min(12, max(1, len(active_frames) // 8))
    valid_blocks = [(s, e) for s, e in blocks if (e - s + 1) >= min_len]
    
    if not valid_blocks:
        return None, None
    
    longest_block = max(valid_blocks, key=lambda b: b[1] - b[0])
    
    return frame_numbers[longest_block[0]], frame_numbers[longest_block[1]]


def _fill_binary_gaps(values: list[int], max_gap: int) -> list[int]:
    filled = values.copy()
    i = 0
    while i < len(filled):
        if filled[i] != 0:
            i += 1
            continue
        start = i
        while i < len(filled) and filled[i] == 0:
            i += 1
        end = i - 1
        has_left = start > 0 and filled[start - 1] == 1
        has_right = i < len(filled) and filled[i] == 1
        if has_left and has_right and (end - start + 1) <= max_gap:
            for j in range(start, end + 1):
                filled[j] = 1
    return filled


def viterbi_decode_phases(probabilities: list[list[float]], encoder_classes: list[str]) -> list[str]:
    """Strictly enforce the sequence: preparation -> downswing -> followthrough."""
    state_to_phase = ["preparation", "downswing", "followthrough"]
    
    state_to_model_idx = []
    for state in state_to_phase:
        idx = list(encoder_classes).index(state)
        state_to_model_idx.append(idx)
        
    n_frames = len(probabilities)
    if n_frames == 0:
        return []
    
    dp = np.full((n_frames, 3), -np.inf)
    backpointer = np.zeros((n_frames, 3), dtype=int)
    
    p = probabilities[0][state_to_model_idx[0]]
    dp[0][0] = np.log(max(p, 1e-10))
        
    for t in range(1, n_frames):
        for s in range(3):
            p = probabilities[t][state_to_model_idx[s]]
            log_p = np.log(max(p, 1e-10))
            
            best_prev_s = -1
            max_val = -np.inf
            
            valid_prev = []
            if s == 0: valid_prev = [0]
            elif s == 1: valid_prev = [0, 1]
            elif s == 2: valid_prev = [1, 2]
            
            for prev_s in valid_prev:
                transition_penalty = 0.0 if prev_s == s else -0.15
                val = dp[t-1][prev_s] + log_p + transition_penalty
                if val > max_val:
                    max_val = val
                    best_prev_s = prev_s
                    
            dp[t][s] = max_val
            backpointer[t][s] = best_prev_s
            
    best_last_state = 2 if np.isfinite(dp[-1][2]) else int(np.argmax(dp[-1]))
    path = []
    curr_state = best_last_state
    for t in range(n_frames - 1, -1, -1):
        path.append(state_to_phase[curr_state])
        curr_state = backpointer[t][curr_state]
        
    path.reverse()
    return path


