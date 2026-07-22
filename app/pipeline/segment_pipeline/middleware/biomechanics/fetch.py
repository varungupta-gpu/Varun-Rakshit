import logging
import pandas as pd
import numpy as np
from pathlib import Path


# LOGGER CONFIG
logging.basicConfig( level=logging.ERROR,format="%(levelname)s: %(message)s")

REQUIRED_COLUMNS = [

    "frame",

    "tracker_id",

    "nose_x",
    "nose_y",

    "left_shoulder_x",
    "left_shoulder_y",

    "right_shoulder_x",
    "right_shoulder_y",

    "left_elbow_x",
    "left_elbow_y",

    "right_elbow_x",
    "right_elbow_y",

    "left_wrist_x",
    "left_wrist_y",

    "right_wrist_x",
    "right_wrist_y",

    "left_hip_x",
    "left_hip_y",

    "right_hip_x",
    "right_hip_y",

    "left_knee_x",
    "left_knee_y",
    
    "right_knee_x",
    "right_knee_y",

    "left_ankle_x",
    "left_ankle_y",

    "right_ankle_x",
    "right_ankle_y",

]


def fetch_keypoint_data(df: pd.DataFrame, release_frame, df_bowler_keypoints_for_bowling_amr) -> pd.DataFrame:
    """
    Reads CSV, filters valid rows,
    validates required columns,
    and returns clean dataframe.
    """

    # CHECK REQUIRED COLUMNS
    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing columns in CSV: {missing_columns}")

    # KEEP ONLY REQUIRED COLUMNS
    df = df[REQUIRED_COLUMNS].copy()

    # REMOVE EMPTY TRACKING ROWS
    df = df[df["tracker_id"].notna()]

    # REMOVE FULLY ZERO ROWS
    numeric_cols = df.select_dtypes(include="number").columns
    df = df[(df[numeric_cols] != 0).any(axis=1)]

    df = df.dropna(subset=REQUIRED_COLUMNS)

    # Get bowling arm from the release frame
    release_row = df_bowler_keypoints_for_bowling_amr[df_bowler_keypoints_for_bowling_amr["frame"] == release_frame]

    if release_row.empty:
        raise ValueError(f"No row found for release_frame={release_frame}")

    bowling_arm = release_row.iloc[0]["bowling_arm"]

    # Add bowling_arm column to all rows
    df["bowling_arm"] = bowling_arm

    # Compute missing joint angles
    df = calculate_joint_angles(df)

    return df




def calculate_joint_angles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes elbow and knee angles (degrees) for every frame.
    """

    def angle(ax, ay, bx, by, cx, cy):

        ba_x = ax - bx
        ba_y = ay - by

        bc_x = cx - bx
        bc_y = cy - by

        dot = ba_x * bc_x + ba_y * bc_y

        mag_ba = np.sqrt(ba_x**2 + ba_y**2)
        mag_bc = np.sqrt(bc_x**2 + bc_y**2)

        denom = mag_ba * mag_bc
        denom = np.where(denom == 0, np.nan, denom)

        cos_theta = dot / denom
        cos_theta = np.clip(cos_theta, -1.0, 1.0)

        return np.degrees(np.arccos(cos_theta))

    # ---------------- Left Elbow ----------------
    df["left_elbow_angle"] = angle(
        df["left_shoulder_x"], df["left_shoulder_y"],
        df["left_elbow_x"], df["left_elbow_y"],
        df["left_wrist_x"], df["left_wrist_y"],
    )

    # ---------------- Right Elbow ----------------
    df["right_elbow_angle"] = angle(
        df["right_shoulder_x"], df["right_shoulder_y"],
        df["right_elbow_x"], df["right_elbow_y"],
        df["right_wrist_x"], df["right_wrist_y"],
    )

    # ---------------- Left Knee ----------------
    df["left_knee_angle"] = angle(
        df["left_hip_x"], df["left_hip_y"],
        df["left_knee_x"], df["left_knee_y"],
        df["left_ankle_x"], df["left_ankle_y"],
    )

    # ---------------- Right Knee ----------------
    df["right_knee_angle"] = angle(
        df["right_hip_x"], df["right_hip_y"],
        df["right_knee_x"], df["right_knee_y"],
        df["right_ankle_x"], df["right_ankle_y"],
    )

    return df