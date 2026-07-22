"""
Biomechanics Expert Phase Inference
====================================

Infers batting phases (stance, preparation, downswing, follow-through)
from frame-wise biomechanical features using expert reasoning rather than fixed thresholds.

IN-MEMORY ONLY - No file I/O for API integration.

Usage:
    API mode (no files):
        infer_phases_from_downswing(keypoints_df, downswing_predictions)
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Union


class InMemoryBatterPhaseAnalyzer:
    """
    In-memory biomechanics expert analyzer for batting phases.
    
    Uses expert reasoning to identify phase boundaries from biomechanical
    features rather than fixed thresholds. Works with DataFrames only (no file I/O).
    """

    def __init__(self, keypoints_df: pd.DataFrame, downswing_start: int, downswing_end: int):
        """
        Initialize analyzer with keypoints DataFrame and known downswing frames.

        Parameters
        ----------
        keypoints_df : pd.DataFrame
            DataFrame with batsman keypoints (COCO format)
        downswing_start : int
            Known downswing start frame
        downswing_end : int
            Known downswing end frame
        """
        self.ds_start = downswing_start
        self.ds_end = downswing_end
        self.df = keypoints_df.copy()
        self.features = None
        self.stance_start = None
        self.stance_end = None
        self.trigger_start = None
        self.trigger_end = None
        self.trigger_detected = False
        self.trigger_confidence = "Low"
        self.prep_start = None
        self.prep_end = None
        self.follow_start = None
        self.follow_end = None

    def validate_keypoints(self):
        """Validate keypoints DataFrame."""
        # Handle different frame column names
        frame_col = None
        for col in ['frame', 'frame_no', 'Frame']:
            if col in self.df.columns:
                frame_col = col
                break
        
        if frame_col is None:
            raise ValueError(f"No frame column found. Available: {self.df.columns.tolist()}")
        
        if frame_col != 'frame':
            self.df = self.df.rename(columns={frame_col: 'frame'})
        
        required_keypoints = [
            'nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear',
            'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
            'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
            'left_knee', 'right_knee', 'left_ankle', 'right_ankle'
        ]
        
        missing = []
        for kp in required_keypoints:
            if f'{kp}_x' not in self.df.columns or f'{kp}_y' not in self.df.columns:
                missing.append(kp)
        
        if missing:
            raise ValueError(f"Missing keypoints: {missing}")
        
        self.df = self.df.sort_values('frame').reset_index(drop=True)
        return self.df

    def compute_features(self):
        """Compute biomechanical features from COCO keypoints for phase inference."""
        df = self.df.copy()
        features = pd.DataFrame()
        features["frame"] = df["frame"]

        # Helper functions
        def point(name, side=None):
            if side is None:
                return np.column_stack((df[f"{name}_x"], df[f"{name}_y"]))
            return np.column_stack((df[f"{side}_{name}_x"], df[f"{side}_{name}_y"]))

        def distance(p1, p2):
            return np.linalg.norm(p1 - p2, axis=1)

        def angle(p1, p2):
            return np.degrees(np.arctan2(p2[:, 1] - p1[:, 1], p2[:, 0] - p1[:, 0]))

        def joint_angle(a, b, c):
            ba = a - b
            bc = c - b
            dot = np.sum(ba * bc, axis=1)
            norm = np.linalg.norm(ba, axis=1) * np.linalg.norm(bc, axis=1)
            cosine = np.clip(dot / (norm + 1e-8), -1, 1)
            return np.degrees(np.arccos(cosine))

        # Keypoints
        ls = point("shoulder", "left")
        rs = point("shoulder", "right")
        le = point("elbow", "left")
        re = point("elbow", "right")
        lw = point("wrist", "left")
        rw = point("wrist", "right")
        lh = point("hip", "left")
        rh = point("hip", "right")
        lk = point("knee", "left")
        rk = point("knee", "right")
        la = point("ankle", "left")
        ra = point("ankle", "right")
        nose = point("nose")

        # Upper body features (used in deviation calculation)
        features["left_elbow_angle"] = joint_angle(ls, le, lw)
        features["right_elbow_angle"] = joint_angle(rs, re, rw)
        features["left_arm_extension"] = distance(ls, lw)
        features["right_arm_extension"] = distance(rs, rw)
        features["shoulder_angle"] = angle(ls, rs)

        # Core features (used in deviation calculation)
        features["hip_angle"] = angle(lh, rh)
        features["hip_shoulder_separation"] = features["shoulder_angle"] - features["hip_angle"]
        
        shoulder_center = (ls + rs) / 2
        hip_center = (lh + rh) / 2
        features["trunk_lean"] = angle(hip_center, shoulder_center)
        
        body_center = (shoulder_center + hip_center) / 2
        features["body_center_x"] = body_center[:, 0]
        features["body_center_y"] = body_center[:, 1]

        # Leg features (used in deviation calculation)
        features["left_knee_angle"] = joint_angle(lh, lk, la)
        features["right_knee_angle"] = joint_angle(rh, rk, ra)

        # Head features (used in deviation calculation)
        features["head_x"] = nose[:, 0]
        features["head_y"] = nose[:, 1]

        # Foot features (used in deviation calculation)
        left_disp = np.zeros(len(df))
        right_disp = np.zeros(len(df))
        left_disp[1:] = np.linalg.norm(la[1:] - la[:-1], axis=1)
        right_disp[1:] = np.linalg.norm(ra[1:] - ra[:-1], axis=1)
        features["left_foot_disp"] = left_disp
        features["right_foot_disp"] = right_disp

        features["stance_width"] = distance(la, ra)
        features["stance_width_change"] = features["stance_width"].diff().fillna(0).abs()

        left_dir = np.zeros(len(df))
        right_dir = np.zeros(len(df))
        left_dir[1:] = np.degrees(np.arctan2(la[1:, 1] - la[:-1, 1], la[1:, 0] - la[:-1, 0]))
        right_dir[1:] = np.degrees(np.arctan2(ra[1:, 1] - ra[:-1, 1], ra[1:, 0] - ra[:-1, 0]))
        features["left_foot_direction"] = left_dir
        features["right_foot_direction"] = right_dir

        foot_center = (la + ra) / 2
        foot_disp = np.zeros(len(df))
        foot_disp[1:] = np.linalg.norm(foot_center[1:] - foot_center[:-1], axis=1)
        features["foot_center_disp"] = foot_disp

        self.features = features
        return self.features

    def compute_body_deviation(self):
        """Compute body-region deviation scores from biomechanical features."""
        f = self.features.copy()

        def abs_diff(series):
            return series.diff().abs().fillna(0)

        # Upper body deviation
        upper_features = [
            "left_elbow_angle", "right_elbow_angle",
            "left_arm_extension", "right_arm_extension",
            "shoulder_angle",
        ]
        upper_dev = np.zeros(len(f))
        for col in upper_features:
            upper_dev += abs_diff(f[col])
        upper_dev /= len(upper_features)

        # Core deviation
        core_features = [
            "trunk_lean", "hip_angle", "shoulder_angle", "hip_shoulder_separation",
        ]
        core_dev = np.zeros(len(f))
        for col in core_features:
            core_dev += abs_diff(f[col])
        body_dx = abs_diff(f["body_center_x"])
        body_dy = abs_diff(f["body_center_y"])
        body_disp = np.sqrt(body_dx**2 + body_dy**2)
        core_dev += body_disp
        core_dev /= (len(core_features) + 1)

        # Leg deviation
        leg_features = ["left_knee_angle", "right_knee_angle"]
        leg_dev = np.zeros(len(f))
        for col in leg_features:
            leg_dev += abs_diff(f[col])
        leg_dev /= len(leg_features)

        # Head deviation
        head_dx = abs_diff(f["head_x"])
        head_dy = abs_diff(f["head_y"])
        head_dev = np.sqrt(head_dx**2 + head_dy**2)

        # Foot deviation
        foot_features = [
            "left_foot_disp", "right_foot_disp",
            "stance_width_change", "foot_center_disp",
        ]
        foot_dev = np.zeros(len(f))
        for col in foot_features:
            foot_dev += f[col].fillna(0)
        foot_dev += abs_diff(f["left_foot_direction"])
        foot_dev += abs_diff(f["right_foot_direction"])
        foot_dev /= (len(foot_features) + 2)
        foot_dev = foot_dev * 0.5

        # Overall body deviation
        overall_dev = (upper_dev + core_dev + leg_dev + head_dev + foot_dev) / 5

        # Store
        self.features["upper_body_deviation"] = upper_dev
        self.features["core_deviation"] = core_dev
        self.features["leg_deviation"] = leg_dev
        self.features["head_deviation"] = head_dev
        self.features["foot_deviation"] = foot_dev
        self.features["overall_deviation"] = overall_dev

        return self.features

    def find_stance(self, stable_window=4, tolerance=0.20):
        """
        Detect stance phase (moving backwards from preparation start).
        Maximum duration: 18 frames.
        """
        deviation = self.features["overall_deviation"].values

        stance_start = 0
        stance_end = self.prep_start - 1

        if stance_end < 0:
            self.stance_start = 0
            self.stance_end = -1
            return (0, -1)

        max_stance_frames = 18
        stance_duration = stance_end - stance_start + 1
        
        if stance_duration > max_stance_frames:
            stance_start = stance_end - max_stance_frames + 1
            
        self.stance_start = stance_start
        self.stance_end = stance_end

        return (self.stance_start, self.stance_end)

    def detect_trigger_movement(self, trigger_window=10):
        """Trigger detection is DISABLED."""
        self.trigger_detected = False
        return

    def find_preparation(self, stable_window=4, tolerance=0.20):
        """
        Detect preparation phase by moving backwards from downswing start.
        Minimum duration: 7 frames at 30 FPS (scaled by actual FPS).
        """
        upper_dev = self.features["upper_body_deviation"].values
        core_dev = self.features["core_deviation"].values
        leg_dev = self.features["leg_deviation"].values
        head_dev = self.features["head_deviation"].values
        foot_dev = self.features["foot_deviation"].values * 0.1
        
        prep_deviation = (upper_dev + core_dev + leg_dev + head_dev + foot_dev) / 5

        prep_end = self.ds_start - 1
        
        fps = 30
        if 'fps' in self.df.columns:
            fps_val = self.df['fps'].iloc[0]
            if fps_val and fps_val > 0:
                fps = fps_val
        
        min_prep_frames = int(round(7 * (fps / 30)))

        current = prep_end

        while current >= stable_window:
            window = prep_deviation[current - stable_window + 1 : current + 1]
            std_dev = window.std()

            if std_dev < tolerance:
                prep_start_candidate = current + 1
                prep_duration = prep_end - prep_start_candidate + 1
                
                if prep_duration >= min_prep_frames:
                    self.prep_start = prep_start_candidate
                    self.prep_end = prep_end
                    return (self.prep_start, self.prep_end)

            current -= 1

        prep_start_candidate = max(0, prep_end - min_prep_frames + 1)
        self.prep_start = prep_start_candidate
        self.prep_end = prep_end

        return (self.prep_start, self.prep_end)

    def find_followthrough(self, stable_window=4, tolerance=0.20):
        """
        Detect follow-through phase (moving forward from downswing end).
        Minimum duration: 10 frames.
        """
        upper_dev = self.features["upper_body_deviation"].values
        core_dev = self.features["core_deviation"].values
        leg_dev = self.features["leg_deviation"].values
        head_dev = self.features["head_deviation"].values
        
        followthrough_deviation = (upper_dev + core_dev + leg_dev + head_dev) / 4

        follow_start = self.ds_end + 1

        if follow_start >= len(followthrough_deviation):
            self.follow_start = -1
            self.follow_end = -1
            return (-1, -1)

        min_followthrough_frames = 10

        current = follow_start

        while current <= len(followthrough_deviation) - stable_window:
            window = followthrough_deviation[current : current + stable_window]
            std_dev = window.std()

            if std_dev < tolerance:
                follow_duration = current - 1 - follow_start + 1
                
                if follow_duration >= min_followthrough_frames:
                    self.follow_start = follow_start
                    self.follow_end = current - 1
                    return (self.follow_start, self.follow_end)

            current += 1

        follow_end_candidate = min(follow_start + min_followthrough_frames - 1, len(followthrough_deviation) - 1)
        self.follow_start = follow_start
        self.follow_end = follow_end_candidate

        return (self.follow_start, self.follow_end)

    def infer_phases(self):
        """
        Complete phase detection pipeline.

        Returns
        -------
        dict
            Dictionary with all detected phases
        """
        self.validate_keypoints()

        if self.features is None:
            self.compute_features()

        if "overall_deviation" not in self.features.columns:
            self.compute_body_deviation()

        # Find phases in order
        self.find_preparation()
        self.find_stance()
        self.detect_trigger_movement()
        self.find_followthrough()

        # Build results
        total_frames = len(self.df)

        results = {
            "stance": {
                "start": self.stance_start,
                "end": self.stance_end,
            },
            "trigger": {
                "detected": self.trigger_detected,
                "start": self.trigger_start if self.trigger_detected else None,
                "end": self.trigger_end if self.trigger_detected else None,
                "confidence": self.trigger_confidence,
            },
            "preparation": {
                "start": self.prep_start,
                "end": self.prep_end,
            },
            "downswing": {
                "start": self.ds_start,
                "end": self.ds_end,
            },
            "followthrough": {
                "start": self.follow_start,
                "end": self.follow_end,
            },
            "total_frames": total_frames,
        }

        return results


def infer_phases_from_downswing(
    keypoints_df: pd.DataFrame,
    downswing_predictions: Union[pd.DataFrame, dict, list]
) -> pd.DataFrame:
    """
    IN-MEMORY phase inference - NO FILE I/O.
    
    This is the API-compatible function for batting pipeline integration.
    Takes DataFrames/dicts as input, returns DataFrame directly.
    
    Parameters
    ----------
    keypoints_df : pd.DataFrame
        DataFrame with batsman keypoints (COCO format)
        Required columns: frame, nose_x, nose_y, left_shoulder_x, etc.
    downswing_predictions : pd.DataFrame, dict, or list
        Downswing predictions from phase classification model
        Can be:
        - DataFrame with columns: frame, downswing (0/1) or predicted_phase
        - Dict with frame numbers as keys
        - List of frame numbers where downswing occurs
    
    Returns
    -------
    pd.DataFrame
        DataFrame with batting phases:
        Columns: phase, start_frame, end_frame, duration, confidence
        Rows: stance, preparation, downswing, followthrough (and optionally trigger)
    
    Example
    -------
    >>> keypoints_df = pd.read_csv("batsman_keypoints.csv")
    >>> downswing_preds = predict_phases(keypoints_df)
    >>> phases_df = infer_phases_from_downswing(keypoints_df, downswing_preds)
    >>> print(phases_df)
         phase  start_frame  end_frame  duration confidence
    0   stance            0         45        46       high
    1   preparation      46         67        22       high
    2   downswing        68         78        11       high
    3   followthrough    79        120        42       high
    """
    
    # ================================================================
    # STEP 1: Extract downswing start/end from predictions
    # ================================================================
    
    if isinstance(downswing_predictions, pd.DataFrame):
        # DataFrame format
        if 'downswing' in downswing_predictions.columns:
            # Binary column: downswing = 1
            downswing_mask = downswing_predictions['downswing'] == 1
            downswing_frames = downswing_predictions[downswing_mask]['frame'].values
        elif 'predicted_phase' in downswing_predictions.columns:
            # Categorical column: predicted_phase = 'downswing'
            downswing_mask = downswing_predictions['predicted_phase'].str.lower() == 'downswing'
            frame_col = 'frame_no' if 'frame_no' in downswing_predictions.columns else 'frame'
            downswing_frames = downswing_predictions[downswing_mask][frame_col].values
        else:
            raise ValueError("downswing_predictions DataFrame must have 'downswing' or 'predicted_phase' column")
            
    elif isinstance(downswing_predictions, dict):
        # Dict format: {frame: prediction}
        downswing_frames = [f for f, pred in downswing_predictions.items() if pred == 1 or pred == 'downswing']
        
    elif isinstance(downswing_predictions, (list, np.ndarray)):
        # List format: [frame1, frame2, ...]
        downswing_frames = downswing_predictions
        
    else:
        raise TypeError(f"downswing_predictions must be DataFrame, dict, or list, got {type(downswing_predictions)}")
    
    if len(downswing_frames) == 0:
        raise ValueError("No downswing frames found in predictions")
    
    ds_start = int(np.min(downswing_frames))
    ds_end = int(np.max(downswing_frames))
    
    # ================================================================
    # STEP 2: Run phase inference using in-memory analyzer
    # ================================================================
    
    analyzer = InMemoryBatterPhaseAnalyzer(keypoints_df, ds_start, ds_end)
    phase_results = analyzer.infer_phases()
    
    # ================================================================
    # STEP 3: Convert results to DataFrame (NO CSV SAVE)
    # ================================================================
    
    rows = []
    
    for phase_name in ("stance", "preparation", "downswing", "followthrough"):
        phase_info = phase_results.get(phase_name) or {}
        start = phase_info.get("start")
        end = phase_info.get("end")
        
        if start is None or end is None or start < 0 or end < 0:
            continue
        
        duration = end - start + 1
        confidence = "high" if duration > 5 else "medium" if duration > 2 else "low"
        
        rows.append({
            "phase": phase_name,
            "start_frame": int(start),
            "end_frame": int(end),
            "duration": duration,
            "confidence": confidence
        })
    
    # Add trigger if detected
    trigger = phase_results.get("trigger") or {}
    if trigger.get("detected") and trigger.get("start") is not None and trigger.get("end") is not None:
        trigger_start = int(trigger["start"])
        trigger_end = int(trigger["end"])
        trigger_duration = trigger_end - trigger_start + 1
        
        rows.append({
            "phase": "trigger",
            "start_frame": trigger_start,
            "end_frame": trigger_end,
            "duration": trigger_duration,
            "confidence": trigger.get("confidence", "low").lower()
        })
    
    # Return DataFrame directly (NO CSV SAVE)
    phases_df = pd.DataFrame(rows)
    
    return phases_df
