"""
Biomechanical Feature Computation - Frame-by-Frame
===================================================

Computes biomechanical features frame-by-frame throughout the entire batting action
from stance start to follow-through end.

All functions return arrays/series with one value per frame in the specified range.

IMPORTANT: This module computes phase-specific biomechanical features.
For general frame-by-frame features during prediction, use extract_shot_features.py
"""

import numpy as np
import pandas as pd


def compute_all_frame_features(df, start_frame, end_frame, stance_start_frame=None, stance_end_frame=None):
    """
    Compute ALL biomechanical features frame-by-frame for a given range.
    
    This is the unified function that computes all features throughout the action.
    Returns a DataFrame with one row per frame containing all features.
    
    Parameters
    ----------
    df : pandas.DataFrame
        Keypoints dataframe with frame and keypoint columns
    start_frame : int
        Starting frame (typically stance start)
    end_frame : int
        Ending frame (typically follow-through end)
    stance_start_frame : int, optional
        Stance start frame for stance-dependent features
    stance_end_frame : int, optional
        Stance end frame for stance-dependent features
    
    Returns
    -------
    pandas.DataFrame
        Frame-by-frame features with columns:
        - frame
        - All biomechanical features (one value per frame)
    """
    segment = df[(df["frame"] >= start_frame) & (df["frame"] <= end_frame)].copy()
    
    if len(segment) == 0:
        return pd.DataFrame()
    
    # Use stance range if provided, otherwise use first few frames as baseline
    if stance_start_frame is None:
        stance_start_frame = start_frame
    if stance_end_frame is None:
        stance_end_frame = min(start_frame + 10, end_frame)
    
    features_df = pd.DataFrame()
    features_df['frame'] = segment['frame'].values
    
    # === HIP & SHOULDER FEATURES ===
    features_df['hip_direction'] = compute_hip_direction(df, start_frame, end_frame).values
    features_df['hip_shoulder_alignment'] = compute_hip_shoulder_alignment(df, start_frame, end_frame).values
    features_df['shoulder_tilt'] = compute_shoulder_tilt(df, start_frame, end_frame).values
    features_df['shoulder_tilt_progression'] = compute_shoulder_tilt_progression(df, start_frame, end_frame).values
    
    # === HEAD FEATURES ===
    features_df['head_stability'] = compute_head_stability(
        df, start_frame, end_frame, stance_start_frame, stance_end_frame
    ).values
    
    # === KNEE FEATURES ===
    features_df['front_knee_angle'] = compute_front_knee_angle(df, start_frame, end_frame).values
    features_df['back_knee_angle'] = compute_back_knee_angle(df, start_frame, end_frame).values
    
    # === STRIDE & STANCE ===
    features_df['stride_width'] = compute_stride_width(df, start_frame, end_frame).values
    
    # === TRUNK FEATURES ===
    features_df['trunk_lateral_flexion'] = compute_trunk_lateral_flexion(df, start_frame, end_frame).values
    
    # === ARM FEATURES ===
    features_df['dominant_shoulder_elbow_line'] = compute_dominant_shoulder_elbow_line(df, start_frame, end_frame).values
    features_df['nondominant_shoulder_elbow_line'] = compute_nondominant_shoulder_elbow_line(df, start_frame, end_frame).values
    features_df['dominant_elbow_wrist_line'] = compute_dominant_elbow_wrist_line(df, start_frame, end_frame).values
    features_df['nondominant_elbow_wrist_line'] = compute_nondominant_elbow_wrist_line(df, start_frame, end_frame).values
    
    # === FOOT FEATURES ===
    features_df['front_foot_ankle_knee_line'] = compute_front_foot_ankle_knee_line(df, start_frame, end_frame).values
    features_df['back_foot_ankle_knee_line'] = compute_back_foot_ankle_knee_line(df, start_frame, end_frame).values
    features_df['front_foot_progression'] = compute_front_foot_progression(
        df, start_frame, end_frame, stance_start_frame, stance_end_frame
    ).values
    features_df['back_foot_progression'] = compute_back_foot_progression(
        df, start_frame, end_frame, stance_start_frame, stance_end_frame
    ).values
    features_df['front_foot_movement_angle'] = compute_front_foot_movement_angle(
        df, start_frame, end_frame, stance_start_frame, stance_end_frame
    ).values
    features_df['back_foot_movement_angle'] = compute_back_foot_movement_angle(
        df, start_frame, end_frame, stance_start_frame, stance_end_frame
    ).values
    
    # === CENTER OF MASS & ROTATION ===
    features_df['weighted_com'] = compute_weighted_com(
        df, start_frame, end_frame, stance_start_frame, stance_end_frame
    ).values
    features_df['upper_body_rotation'] = compute_upper_body_rotation(
        df, start_frame, end_frame, stance_start_frame, stance_end_frame
    ).values
    features_df['lower_body_rotation'] = compute_lower_body_rotation(
        df, start_frame, end_frame, stance_start_frame, stance_end_frame
    ).values
    
    return features_df


def compute_hip_direction(df, start_frame, end_frame):
    """
    Hip direction (degrees) measured with respect to vertical.
    
    Vertical is defined as the negative Y-axis (upward in video coordinates).
    Computes the angle between the hip line and vertical for each frame.
    
    Returns:
        angle : array
            Angle in degrees where:
            - 0° = hip line perfectly vertical
            - Positive = rotated clockwise from vertical
            - Negative = rotated counter-clockwise from vertical
            - Range: [-90°, 90°]
    """
    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    dx = segment["right_hip_x"] - segment["left_hip_x"]
    dy = segment["right_hip_y"] - segment["left_hip_y"]

    # Compute angle wrt vertical (y-axis pointing up = negative y-direction)
    # Vertical reference: (0, -1)
    # Hip vector: (dx, dy)
    # Angle = atan2(dx, -dy) gives angle from vertical
    hip_direction = np.degrees(np.arctan2(dx, -dy))

    return hip_direction


def compute_hip_shoulder_alignment(df, start_frame, end_frame):
    """
    Hip-Shoulder alignment (degrees).
    
    Computes the angle BETWEEN hip line and shoulder line.
    This shows how much shoulders are rotated relative to hips.
    
    Hip line: left_hip (11) to right_hip (12)
    Shoulder line: left_shoulder (front, 5) to right_shoulder (back, 6)
    
    Angle between these 2 lines = hip-shoulder separation/rotation
    """

    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    # Hip line vectors: right_hip - left_hip (left is front, right is back)
    hip_vec_x = segment["right_hip_x"] - segment["left_hip_x"]
    hip_vec_y = segment["right_hip_y"] - segment["left_hip_y"]
    
    # Shoulder line vectors: right_shoulder - left_shoulder (left is front, right is back)
    shoulder_vec_x = segment["right_shoulder_x"] - segment["left_shoulder_x"]
    shoulder_vec_y = segment["right_shoulder_y"] - segment["left_shoulder_y"]
    
    # Angle between two lines using dot product
    dot_product = hip_vec_x * shoulder_vec_x + hip_vec_y * shoulder_vec_y
    
    # Magnitudes
    hip_mag = np.sqrt(hip_vec_x**2 + hip_vec_y**2)
    shoulder_mag = np.sqrt(shoulder_vec_x**2 + shoulder_vec_y**2)
    
    # Cosine of angle
    cosine = dot_product / (hip_mag * shoulder_mag + 1e-8)
    cosine = np.clip(cosine, -1.0, 1.0)
    
    # Angle between lines (0 to 180)
    alignment = np.degrees(np.arccos(cosine))

    return alignment


def compute_shoulder_tilt_progression(df, start_frame, end_frame):
    """
    Frame-to-frame shoulder tilt change (degrees).
    
    Computes change from PREVIOUS FRAME in entire sequence, not just within phase.
    This gives TRUE frame-by-frame progression across all phases.
    """

    # Get ALL frames (not just the phase range) to compute progression correctly
    all_frames = df.copy().sort_values('frame')
    
    # Calculate shoulder tilt for ALL frames
    shoulder_tilt_all = np.degrees(np.arctan2(
        all_frames["right_shoulder_y"] - all_frames["left_shoulder_y"],
        all_frames["right_shoulder_x"] - all_frames["left_shoulder_x"]
    ))
    
    # Compute frame-to-frame progression for ALL frames
    progression_all = shoulder_tilt_all.diff().fillna(0)
    
    # Extract only the frames in the specified range
    segment_indices = all_frames[(all_frames["frame"] >= start_frame) & 
                                 (all_frames["frame"] <= end_frame)].index
    
    shoulder_tilt_progression = progression_all.loc[segment_indices]

    return shoulder_tilt_progression.values


def compute_shoulder_tilt(df, start_frame, end_frame):
    """Shoulder tilt (degrees).
    
    Note: Left shoulder is front (closer to bowler), right shoulder is back.
    Measures shoulder line from left (front) to right (back).
    """

    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    shoulder_tilt = np.degrees(np.arctan2(
        segment["right_shoulder_y"] - segment["left_shoulder_y"],
        segment["right_shoulder_x"] - segment["left_shoulder_x"]
    ))

    return shoulder_tilt

def compute_head_stability(df, start_frame, end_frame,
                           stance_start_frame, stance_end_frame):
    """Head stability relative to stance."""

    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    stance = df[(df["frame"] >= stance_start_frame) &
                (df["frame"] <= stance_end_frame)]

    head_x = (segment["left_eye_x"] + segment["right_eye_x"]) / 2
    head_y = (segment["left_eye_y"] + segment["right_eye_y"]) / 2

    shoulder_x = (segment["left_shoulder_x"] + segment["right_shoulder_x"]) / 2
    shoulder_y = (segment["left_shoulder_y"] + segment["right_shoulder_y"]) / 2

    rel_x = head_x - shoulder_x
    rel_y = head_y - shoulder_y

    stance_head_x = (((stance["left_eye_x"] + stance["right_eye_x"]) / 2) -
                     ((stance["left_shoulder_x"] + stance["right_shoulder_x"]) / 2)).mean()

    stance_head_y = (((stance["left_eye_y"] + stance["right_eye_y"]) / 2) -
                     ((stance["left_shoulder_y"] + stance["right_shoulder_y"]) / 2)).mean()

    head_stability = np.sqrt((rel_x - stance_head_x) ** 2 +
                             (rel_y - stance_head_y) ** 2)

    return head_stability


def compute_front_knee_angle(df, start_frame, end_frame):
    """Front knee angle (degrees)."""

    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    hip = np.column_stack((segment["left_hip_x"], segment["left_hip_y"]))
    knee = np.column_stack((segment["left_knee_x"], segment["left_knee_y"]))
    ankle = np.column_stack((segment["left_ankle_x"], segment["left_ankle_y"]))

    v1 = hip - knee
    v2 = ankle - knee

    cosine = np.sum(v1 * v2, axis=1) / (
        np.linalg.norm(v1, axis=1) * np.linalg.norm(v2, axis=1)
    )
    cosine = np.clip(cosine, -1.0, 1.0)

    front_knee_angle = np.degrees(np.arccos(cosine))

    return front_knee_angle


def compute_back_knee_angle(df, start_frame, end_frame):
    """Back knee angle (degrees)."""

    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    hip = np.column_stack((segment["right_hip_x"], segment["right_hip_y"]))
    knee = np.column_stack((segment["right_knee_x"], segment["right_knee_y"]))
    ankle = np.column_stack((segment["right_ankle_x"], segment["right_ankle_y"]))

    v1 = hip - knee
    v2 = ankle - knee

    cosine = np.sum(v1 * v2, axis=1) / (
        np.linalg.norm(v1, axis=1) * np.linalg.norm(v2, axis=1)
    )
    cosine = np.clip(cosine, -1.0, 1.0)

    back_knee_angle = np.degrees(np.arccos(cosine))

    return back_knee_angle


def compute_stride_width(df, start_frame, end_frame):
    """Stride width (pixels)."""

    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    stride_width = np.sqrt(
        (segment["left_ankle_x"] - segment["right_ankle_x"]) ** 2 +
        (segment["left_ankle_y"] - segment["right_ankle_y"]) ** 2
    )

    return stride_width
def compute_trunk_lateral_flexion(df, start_frame, end_frame,
                                   stance_start_frame=None, stance_end_frame=None):
    """
    Trunk lateral flexion change relative to stance (degrees).
    
    Measures the change in trunk lean from the stance baseline.
    Computes trunk angle from vertical at each frame and compares to stance.
    
    REFERENCE FRAME: Average trunk angle during stance phase
    (stance_start_frame to stance_end_frame)
    
    Returns
    -------
    flexion_change : array
        Trunk flexion change in degrees where:
        - 0° = same lean as stance
        - Positive = increased forward lean relative to stance
        - Negative = increased backward lean relative to stance
        
    Range typically: -30° to +30° (showing how much trunk moved from stance position)
    """

    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    # Get current trunk angles for each frame
    shoulder_x = (segment["left_shoulder_x"] + segment["right_shoulder_x"]) / 2
    shoulder_y = (segment["left_shoulder_y"] + segment["right_shoulder_y"]) / 2

    hip_x = (segment["left_hip_x"] + segment["right_hip_x"]) / 2
    hip_y = (segment["left_hip_y"] + segment["right_hip_y"]) / 2

    trunk_x = shoulder_x - hip_x
    trunk_y = shoulder_y - hip_y

    current_trunk_angle = np.degrees(np.arctan2(trunk_x, -trunk_y))

    # If stance frames not provided, use first few frames as baseline
    if stance_start_frame is None or stance_end_frame is None:
        stance_start_frame = start_frame
        stance_end_frame = min(start_frame + 10, end_frame)

    # Get stance trunk angle (baseline reference)
    stance = df[(df["frame"] >= stance_start_frame) &
                (df["frame"] <= stance_end_frame)]
    
    stance_shoulder_x = ((stance["left_shoulder_x"] + stance["right_shoulder_x"]) / 2).mean()
    stance_shoulder_y = ((stance["left_shoulder_y"] + stance["right_shoulder_y"]) / 2).mean()
    stance_hip_x = ((stance["left_hip_x"] + stance["right_hip_x"]) / 2).mean()
    stance_hip_y = ((stance["left_hip_y"] + stance["right_hip_y"]) / 2).mean()

    stance_trunk_x = stance_shoulder_x - stance_hip_x
    stance_trunk_y = stance_shoulder_y - stance_hip_y
    stance_trunk_angle = np.degrees(np.arctan2(stance_trunk_x, -stance_trunk_y))

    # Compute change from stance
    flexion_change = current_trunk_angle - stance_trunk_angle

    return flexion_change


def compute_dominant_shoulder_elbow_line(df, start_frame, end_frame):
    """
    Dominant arm elbow joint angle (degrees).
    
    Measures the angle AT THE ELBOW between shoulder-elbow-wrist.
    This is the actual joint angle showing arm bend/extension.
    
    Keypoints: shoulder (6) → elbow (8) → wrist (10)
    """

    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    # Get coordinates
    shoulder = np.column_stack((segment["right_shoulder_x"], segment["right_shoulder_y"]))
    elbow = np.column_stack((segment["right_elbow_x"], segment["right_elbow_y"]))
    wrist = np.column_stack((segment["right_wrist_x"], segment["right_wrist_y"]))

    # Vectors from elbow
    ba = shoulder - elbow  # vector from elbow to shoulder
    bc = wrist - elbow     # vector from elbow to wrist

    # Angle at elbow joint using dot product
    dot = np.sum(ba * bc, axis=1)
    norm = np.linalg.norm(ba, axis=1) * np.linalg.norm(bc, axis=1)
    cosine = np.clip(dot / (norm + 1e-8), -1.0, 1.0)
    
    elbow_joint_angle = np.degrees(np.arccos(cosine))

    return elbow_joint_angle


def compute_nondominant_shoulder_elbow_line(df, start_frame, end_frame):
    """
    Non-dominant arm elbow joint angle (degrees).
    
    Measures the angle AT THE ELBOW between shoulder-elbow-wrist.
    This is the actual joint angle showing arm bend/extension.
    
    Keypoints: shoulder (5) → elbow (7) → wrist (9)
    """

    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    # Get coordinates
    shoulder = np.column_stack((segment["left_shoulder_x"], segment["left_shoulder_y"]))
    elbow = np.column_stack((segment["left_elbow_x"], segment["left_elbow_y"]))
    wrist = np.column_stack((segment["left_wrist_x"], segment["left_wrist_y"]))

    # Vectors from elbow
    ba = shoulder - elbow  # vector from elbow to shoulder
    bc = wrist - elbow     # vector from elbow to wrist

    # Angle at elbow joint using dot product
    dot = np.sum(ba * bc, axis=1)
    norm = np.linalg.norm(ba, axis=1) * np.linalg.norm(bc, axis=1)
    cosine = np.clip(dot / (norm + 1e-8), -1.0, 1.0)
    
    elbow_joint_angle = np.degrees(np.arccos(cosine))

    return elbow_joint_angle


def compute_dominant_elbow_wrist_line(df, start_frame, end_frame):
    """
    Dominant elbow-wrist arm line (degrees).
    
    Angle measured from WRIST → ELBOW (left to right for right-arm).
    This makes visualization intuitive: wrist on left, elbow on right.
    """

    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    # Changed: elbow - wrist (instead of wrist - elbow) for intuitive left-to-right measurement
    dominant_elbow_wrist_line = np.degrees(np.arctan2(
        segment["right_elbow_y"] - segment["right_wrist_y"],
        segment["right_elbow_x"] - segment["right_wrist_x"]
    ))

    return dominant_elbow_wrist_line

def compute_nondominant_elbow_wrist_line(df, start_frame, end_frame):
    """
    Non-dominant elbow-wrist arm line (degrees).
    
    Angle measured from WRIST → ELBOW (right to left for left-arm).
    This makes visualization intuitive: wrist on right, elbow on left.
    """

    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    # Changed: elbow - wrist (instead of wrist - elbow) for intuitive right-to-left measurement
    nondominant_elbow_wrist_line = np.degrees(np.arctan2(
        segment["left_elbow_y"] - segment["left_wrist_y"],
        segment["left_elbow_x"] - segment["left_wrist_x"]
    ))

    return nondominant_elbow_wrist_line


def compute_front_foot_ankle_knee_line(df, start_frame, end_frame):
    """Front foot ankle-knee line orientation (degrees)."""

    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    front_foot_ankle_knee_line = np.degrees(np.arctan2(
        segment["left_ankle_y"] - segment["left_knee_y"],
        segment["left_ankle_x"] - segment["left_knee_x"]
    ))

    return front_foot_ankle_knee_line


def compute_back_foot_ankle_knee_line(df, start_frame, end_frame):
    """Back foot ankle-knee line orientation (degrees)."""

    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    back_foot_ankle_knee_line = np.degrees(np.arctan2(
        segment["right_ankle_y"] - segment["right_knee_y"],
        segment["right_ankle_x"] - segment["right_knee_x"]
    ))

    return back_foot_ankle_knee_line


def compute_eye_line_angle(df, start_frame, end_frame):
    """
    Eye line orientation (degrees).

    Note:
    COCO keypoints do not include stumps.
    This computes only the eye-line orientation.
    """

    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    eye_line_angle = np.degrees(np.arctan2(
        segment["right_eye_y"] - segment["left_eye_y"],
        segment["right_eye_x"] - segment["left_eye_x"]
    ))

    return eye_line_angle

def compute_front_foot_progression(df, start_frame, end_frame,
                                   stance_start_frame, stance_end_frame):
    """
    Front foot signed progression normalized by stance stride width.
    
    Measures SIGNED displacement along the stride axis (forward/backward direction).
    
    Returns
    -------
    progression : array
        Signed progression where:
        - Positive = foot moving forward (in batting direction)
        - Negative = foot moving backward
        - 0 = no movement along stride axis
        
    Example:
        +0.5 = moved 50% of stride width forward
        -0.3 = moved 30% of stride width backward
    """

    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    stance = df[(df["frame"] >= stance_start_frame) &
                (df["frame"] <= stance_end_frame)]

    # Get stance baseline positions
    stance_front_x = stance["left_ankle_x"].mean()
    stance_front_y = stance["left_ankle_y"].mean()
    stance_back_x = stance["right_ankle_x"].mean()
    stance_back_y = stance["right_ankle_y"].mean()

    # Define stride vector (reference axis): back_foot → front_foot
    # This is the "forward" direction in the batting action
    stride_vec_x = stance_front_x - stance_back_x
    stride_vec_y = stance_front_y - stance_back_y
    
    # Stride width (magnitude)
    stride_width = np.sqrt(stride_vec_x**2 + stride_vec_y**2)
    
    # Normalize stride vector to unit vector
    stride_unit_x = stride_vec_x / stride_width
    stride_unit_y = stride_vec_y / stride_width

    # Current front foot displacement from stance
    dx = segment["left_ankle_x"] - stance_front_x
    dy = segment["left_ankle_y"] - stance_front_y

    # Project displacement onto stride axis (dot product with unit stride vector)
    # Positive = moving along stride direction (forward)
    # Negative = moving opposite to stride direction (backward)
    signed_progression = (dx * stride_unit_x + dy * stride_unit_y) / stride_width

    return signed_progression


def compute_back_foot_progression(df, start_frame, end_frame,
                                  stance_start_frame, stance_end_frame):
    """
    Back foot signed progression normalized by stance stride width.
    
    Measures SIGNED displacement along the stride axis (forward/backward direction).
    
    Returns
    -------
    progression : array
        Signed progression where:
        - Positive = foot moving forward (in batting direction)
        - Negative = foot moving backward
        - 0 = no movement along stride axis
        
    Example:
        +0.5 = moved 50% of stride width forward
        -0.3 = moved 30% of stride width backward
    """

    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    stance = df[(df["frame"] >= stance_start_frame) &
                (df["frame"] <= stance_end_frame)]

    # Get stance baseline positions
    stance_front_x = stance["left_ankle_x"].mean()
    stance_front_y = stance["left_ankle_y"].mean()
    stance_back_x = stance["right_ankle_x"].mean()
    stance_back_y = stance["right_ankle_y"].mean()

    # Define stride vector (reference axis): back_foot → front_foot
    # This is the "forward" direction in the batting action
    stride_vec_x = stance_front_x - stance_back_x
    stride_vec_y = stance_front_y - stance_back_y
    
    # Stride width (magnitude)
    stride_width = np.sqrt(stride_vec_x**2 + stride_vec_y**2)
    
    # Normalize stride vector to unit vector
    stride_unit_x = stride_vec_x / stride_width
    stride_unit_y = stride_vec_y / stride_width

    # Current back foot displacement from stance
    dx = segment["right_ankle_x"] - stance_back_x
    dy = segment["right_ankle_y"] - stance_back_y

    # Project displacement onto stride axis (dot product with unit stride vector)
    # Positive = moving along stride direction (forward)
    # Negative = moving opposite to stride direction (backward)
    signed_progression = (dx * stride_unit_x + dy * stride_unit_y) / stride_width

    return signed_progression


 


def compute_weighted_com(df, start_frame, end_frame,
                         stance_start_frame, stance_end_frame):
    """Weighted COM shift from stance."""

    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    stance = df[(df["frame"] >= stance_start_frame) &
                (df["frame"] <= stance_end_frame)]

    shoulder_x = (segment["left_shoulder_x"] + segment["right_shoulder_x"]) / 2
    shoulder_y = (segment["left_shoulder_y"] + segment["right_shoulder_y"]) / 2

    hip_x = (segment["left_hip_x"] + segment["right_hip_x"]) / 2
    hip_y = (segment["left_hip_y"] + segment["right_hip_y"]) / 2

    knee_x = (segment["left_knee_x"] + segment["right_knee_x"]) / 2
    knee_y = (segment["left_knee_y"] + segment["right_knee_y"]) / 2

    com_x = 0.25 * shoulder_x + 0.45 * hip_x + 0.30 * knee_x
    com_y = 0.25 * shoulder_y + 0.45 * hip_y + 0.30 * knee_y

    stance_shoulder_x = ((stance["left_shoulder_x"] + stance["right_shoulder_x"]) / 2).mean()
    stance_shoulder_y = ((stance["left_shoulder_y"] + stance["right_shoulder_y"]) / 2).mean()

    stance_hip_x = ((stance["left_hip_x"] + stance["right_hip_x"]) / 2).mean()
    stance_hip_y = ((stance["left_hip_y"] + stance["right_hip_y"]) / 2).mean()

    stance_knee_x = ((stance["left_knee_x"] + stance["right_knee_x"]) / 2).mean()
    stance_knee_y = ((stance["left_knee_y"] + stance["right_knee_y"]) / 2).mean()

    stance_com_x = 0.25 * stance_shoulder_x + 0.45 * stance_hip_x + 0.30 * stance_knee_x
    stance_com_y = 0.25 * stance_shoulder_y + 0.45 * stance_hip_y + 0.30 * stance_knee_y

    weighted_com = np.sqrt((com_x - stance_com_x)**2 +
                           (com_y - stance_com_y)**2)

    return weighted_com


def compute_upper_body_rotation(df, start_frame, end_frame,
                                stance_start_frame, stance_end_frame):
    """Upper body rotation relative to stance."""

    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    stance = df[(df["frame"] >= stance_start_frame) &
                (df["frame"] <= stance_end_frame)]

    shoulder_x = (segment["left_shoulder_x"] + segment["right_shoulder_x"]) / 2
    shoulder_y = (segment["left_shoulder_y"] + segment["right_shoulder_y"]) / 2

    elbow_x = (segment["left_elbow_x"] + segment["right_elbow_x"]) / 2
    elbow_y = (segment["left_elbow_y"] + segment["right_elbow_y"]) / 2

    current_angle = np.degrees(np.arctan2(
        elbow_y - shoulder_y,
        elbow_x - shoulder_x
    ))

    stance_shoulder_x = ((stance["left_shoulder_x"] + stance["right_shoulder_x"]) / 2).mean()
    stance_shoulder_y = ((stance["left_shoulder_y"] + stance["right_shoulder_y"]) / 2).mean()

    stance_elbow_x = ((stance["left_elbow_x"] + stance["right_elbow_x"]) / 2).mean()
    stance_elbow_y = ((stance["left_elbow_y"] + stance["right_elbow_y"]) / 2).mean()

    stance_angle = np.degrees(np.arctan2(
        stance_elbow_y - stance_shoulder_y,
        stance_elbow_x - stance_shoulder_x
    ))

    upper_body_rotation = current_angle - stance_angle

    return upper_body_rotation

def compute_lower_body_rotation(df, start_frame, end_frame,
                                stance_start_frame, stance_end_frame):
    """Lower body rotation relative to stance."""

    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()

    stance = df[(df["frame"] >= stance_start_frame) &
                (df["frame"] <= stance_end_frame)]

    hip_x = (segment["left_hip_x"] + segment["right_hip_x"]) / 2
    hip_y = (segment["left_hip_y"] + segment["right_hip_y"]) / 2

    knee_x = (segment["left_knee_x"] + segment["right_knee_x"]) / 2
    knee_y = (segment["left_knee_y"] + segment["right_knee_y"]) / 2

    current_angle = np.degrees(np.arctan2(
        knee_y - hip_y,
        knee_x - hip_x
    ))

    stance_hip_x = ((stance["left_hip_x"] + stance["right_hip_x"]) / 2).mean()
    stance_hip_y = ((stance["left_hip_y"] + stance["right_hip_y"]) / 2).mean()

    stance_knee_x = ((stance["left_knee_x"] + stance["right_knee_x"]) / 2).mean()
    stance_knee_y = ((stance["left_knee_y"] + stance["right_knee_y"]) / 2).mean()

    stance_angle = np.degrees(np.arctan2(
        stance_knee_y - stance_hip_y,
        stance_knee_x - stance_hip_x
    ))

    lower_body_rotation = current_angle - stance_angle

    return lower_body_rotation


def compute_shoulder_line_progression_angle(df, start_frame, end_frame,
                                            stance_start_frame, stance_end_frame):
    """
    Shoulder line progression angle relative to vertical (degrees).
    
    Measures the angle between the shoulder line and vertical at each frame.
    Vertical is defined as the negative Y-axis (upward in video coordinates).
    
    The shoulder line connects left_shoulder (front, 5) to right_shoulder (back, 6).
    Left shoulder is in front (closer to bowler), right shoulder is at back.
    
    Returns
    -------
    angle : array
        Angle in degrees measured from vertical where:
        - 0° = shoulder line perfectly vertical
        - Positive = rotated clockwise from vertical
        - Negative = rotated counter-clockwise from vertical
        - Range: [-90°, 90°]
        
    This shows the current shoulder orientation relative to vertical at each frame.
    """
    
    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()
    
    # Get shoulder line for each frame
    shoulder_x = segment["right_shoulder_x"] - segment["left_shoulder_x"]
    shoulder_y = segment["right_shoulder_y"] - segment["left_shoulder_y"]
    
    # Compute angle wrt vertical (y-axis pointing up = negative y-direction)
    # Vertical reference: (0, -1)
    # Shoulder vector: (shoulder_x, shoulder_y)
    # Angle = atan2(shoulder_x, -shoulder_y) gives angle from vertical
    angle = np.degrees(np.arctan2(shoulder_x, -shoulder_y))
    
    return angle


def compute_stride_line_progression_angle(df, start_frame, end_frame,
                                          stance_start_frame, stance_end_frame):
    """
    Stride line progression angle relative to vertical (degrees).
    
    Measures the angle between the stride line and vertical at each frame.
    Vertical is defined as the negative Y-axis (upward in video coordinates).
    
    The stride line connects left ankle (front) to right ankle (back).
    Left ankle is in front (closer to bowler), right ankle is at back.
    
    Returns
    -------
    stride_angle : array
        Angle in degrees measured from vertical where:
        - 0° = stride line perfectly vertical
        - Positive = rotated clockwise from vertical
        - Negative = rotated counter-clockwise from vertical
        - Range: [-90°, 90°]
        
    This shows the current orientation of the feet/stride relative to vertical.
    """
    
    segment = df[(df["frame"] >= start_frame) &
                 (df["frame"] <= end_frame)].copy()
    
    # Get stride line for each frame
    # Stride line: left (front) ankle to right (back) ankle
    stride_vec_x = segment["right_ankle_x"] - segment["left_ankle_x"]
    stride_vec_y = segment["right_ankle_y"] - segment["left_ankle_y"]
    
    # Compute angle wrt vertical (y-axis pointing up = negative y-direction)
    # Vertical reference: (0, -1)
    # Stride vector: (stride_vec_x, stride_vec_y)
    # Angle = atan2(stride_vec_x, -stride_vec_y) gives angle from vertical
    stride_angle = np.degrees(np.arctan2(stride_vec_x, -stride_vec_y))
    
    return stride_angle
