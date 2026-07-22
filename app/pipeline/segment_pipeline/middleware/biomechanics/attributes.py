import pandas as pd
import numpy as np


def hip_direction_as_bowler_loadsup(df: pd.DataFrame, phase_name: str):
    """
    Computes hip loading / tilt direction metrics
    for a specific bowling phase.

    Parameters
    ----------
    df : pd.DataFrame
        Full biomechanics dataframe

    phase_name : str
        Example:
        - "Gather Phase"
        - "Backfoot Phase"
        - "Delivery Stride"
        - "Frontfoot Phase"
        - "Follow Through"

    """

    # STEP 1 : FILTER PHASE
    phase_df = df[df["phase"] == phase_name].copy()

    if phase_df.empty:
        raise ValueError(f"No rows found for phase: {phase_name}")

    # STEP 2 : HIP COORDINATES
    xL = phase_df["left_hip_x"]
    yL = phase_df["left_hip_y"]
    xR = phase_df["right_hip_x"]
    yR = phase_df["right_hip_y"]

    # STEP 3 : HIP ANGLE : theta = atan2(yR - yL, xR - xL)
    theta_rad = np.arctan2((yR - yL), (xR - xL))
    theta_deg = np.degrees(theta_rad)
    phase_df["hip_theta_deg"] = theta_deg


    # STEP 4 : METRICS
    signed_mean = theta_deg.mean()
    abs_mean = np.abs(theta_deg).mean()
    std_dev = theta_deg.std()
    max_abs = np.abs(theta_deg).max()

    # STEP 5 : DOMINANT SIDE
    positive_frames = (theta_deg > 0).sum()
    negative_frames = (theta_deg < 0).sum()
    total_frames = len(theta_deg)
    left_load_percentage = (positive_frames / total_frames) * 100
    right_load_percentage = (negative_frames / total_frames) * 100

    if left_load_percentage > right_load_percentage:
        dominant_side = "Left Hip Higher"

    elif right_load_percentage > left_load_percentage:
        dominant_side = "Right Hip Higher"

    else:
        dominant_side = "Balanced"

    # STEP 6 : RETURN
    return {
        "phase": phase_name,
        "total_frames": total_frames,
        "signed_mean": signed_mean,
        "abs_mean": abs_mean,
        "std_dev": std_dev,
        "max_abs": max_abs,
        "dominant_side": dominant_side,
        "left_load_percentage": left_load_percentage,
        "right_load_percentage": right_load_percentage
    }

def hip_shoulder_alignment_metrics(df: pd.DataFrame, phase_name: str):
    """
    Computes Hip-Shoulder Alignment metrics
    for a specific bowling phase.
    FORMULAS :
    Shoulder Angle:
    θs = atan2(Yrs - Yls, Xrs - Xls)
    Hip Angle:
    θh = atan2(Yrh - Ylh, Xrh - Xlh)
    Alignment Difference:
    Δθ = θs - θh

    METRICS :
    abs_mean -> mean(abs(Δθ))
    std_dev -> std(Δθ)
    max_abs -> max(abs(Δθ))
    """

    # STEP 1 : FILTER PHASE
    phase_df = df[df["phase"] == phase_name].copy()

    if phase_df.empty:
        raise ValueError(f"No rows found for phase: {phase_name}")

    # STEP 2 : SHOULDER ANGLE
    shoulder_rad = np.arctan2((phase_df["right_shoulder_y"] - phase_df["left_shoulder_y"]), ( phase_df["right_shoulder_x"] - phase_df["left_shoulder_x"]))
    shoulder_deg = np.degrees(shoulder_rad)

    # STEP 3 : HIP ANGLE
    hip_rad = np.arctan2((phase_df["right_hip_y"] - phase_df["left_hip_y"]), (phase_df["right_hip_x"] - phase_df["left_hip_x"]))
    hip_deg = np.degrees(hip_rad)

    # STEP 4 : ALIGNMENT DIFFERENCE : Δθ = θs - θh
    delta_theta = shoulder_deg - hip_deg
    phase_df["shoulder_angle_deg"] = shoulder_deg
    phase_df["hip_angle_deg"] = hip_deg
    phase_df["alignment_delta_deg"] = delta_theta


    # STEP 5 : METRICS
    abs_mean = np.abs(delta_theta).mean()
    std_dev = delta_theta.std()
    max_abs = np.abs(delta_theta).max()

    # STEP 6 : RETURN
    return {
        "phase": phase_name,
        "total_frames": len(phase_df),
        "abs_mean": abs_mean,
        "std_dev": std_dev,
        "max_abs": max_abs
    }

def shoulder_tilt_progression_metrics(df: pd.DataFrame):
    """
    Computes Shoulder Tilt Progression
    from Gather Phase -> Follow Through.

    FORMULA :
    Left Shoulder  = (X_l, Y_l)
    Right Shoulder = (X_r, Y_r)
    tan(theta) = (X_l - X_r)/(Y_l - Y_r)
    theta = atan2((X_l - X_r),(Y_l - Y_r))

    FRAME-TO-FRAME CHANGE : Δθ_i = θ_i - θ_(i-1)

    SMOOTHNESS SCORE :
    S = mean(abs(Δθ))
    Lower S -> smoother shoulder progression
    Higher S -> abrupt / oscillatory motion
    """

    # STEP 1 : REQUIRED PHASES
    required_phases = ["Gather Phase"]

    # STEP 2 : FILTER PHASES
    phase_df = df[df["phase"].isin(required_phases)].copy()

    if phase_df.empty:
        raise ValueError("No required phases found.")

    # STEP 3 : SORT BY FRAME
    phase_df = phase_df.sort_values(by="frame").reset_index(drop=True)

    # STEP 4 : SHOULDER COORDINATES
    X_l = phase_df["left_shoulder_x"]
    Y_l = phase_df["left_shoulder_y"]

    X_r = phase_df["right_shoulder_x"]
    Y_r = phase_df["right_shoulder_y"]

    # STEP 5 : SHOULDER TILT ANGLE

    theta_rad = np.arctan2((X_l - X_r), (Y_l - Y_r))
    theta_deg = np.degrees(theta_rad)
    phase_df["shoulder_tilt_deg"] = theta_deg

    # STEP 6 : FRAME-TO-FRAME CHANGE : Δθ_i = θ_i - θ_(i-1)
    phase_df["delta_theta_deg"] = (phase_df["shoulder_tilt_deg"].diff().fillna(0))


    # STEP 7 : SMOOTHNESS SCORE : S = mean(abs(delta_theta))
    smoothness_score = (np.abs(phase_df["delta_theta_deg"]).mean())

    # STEP 8 : RETURN

    return {
        "total_frames": len(phase_df),
        "delta_theta_sequence": phase_df["delta_theta_deg"].tolist(),
        "smoothness_score": smoothness_score,
        "std_dev_tilt": theta_deg.std()
    }

def head_position_stability_metrics( df: pd.DataFrame, phase_name: str):
    """
    Computes Head Position & Stability
    for a specific bowling phase.
    """

    # STEP 1 : FILTER PHASE
    phase_df = df[df["phase"] == phase_name].copy()

    if phase_df.empty:
        raise ValueError(f"No rows found for phase: {phase_name}")

    # STEP 2 : MID SHOULDER
    phase_df["mid_shoulder_x"] = (phase_df["left_shoulder_x"] + phase_df["right_shoulder_x"]) / 2
    phase_df["mid_shoulder_y"] = (phase_df["left_shoulder_y"] + phase_df["right_shoulder_y"]) / 2

    # STEP 3 : MID HIP
    phase_df["mid_hip_x"] = ( phase_df["left_hip_x"] + phase_df["right_hip_x"]) / 2
    phase_df["mid_hip_y"] = (phase_df["left_hip_y"] + phase_df["right_hip_y"]) / 2

    # STEP 4 : BODY VECTOR SLOPE
    m1 = (phase_df["mid_hip_y"]- phase_df["mid_shoulder_y"]) / (phase_df["mid_hip_x"] - phase_df["mid_shoulder_x"])

    # STEP 5 : HEAD VECTOR SLOPE
    m2 = (phase_df["nose_y"] - phase_df["mid_shoulder_y"]) / (phase_df["nose_x"] - phase_df["mid_shoulder_x"])

    # STEP 6 : ANGLE : theta = atan((m2-m1)/(1+m1*m2))
    theta_rad = np.arctan((m2 - m1)/(1 + (m1 * m2)))
    theta_deg = np.degrees(theta_rad)
    phase_df["head_body_theta_deg"] = theta_deg

    # STEP 7 : METRICS
    signed_mean = theta_deg.mean()
    abs_mean = np.abs(theta_deg).mean()
    std_dev = theta_deg.std()
    max_abs = np.abs(theta_deg).max()

    # STEP 8 : DOMINANT SIDE
    positive_frames = (theta_deg > 0).sum()
    negative_frames = (theta_deg < 0).sum()
    total_frames = len(theta_deg)

    anticlockwise_percentage = (positive_frames / total_frames) * 100
    clockwise_percentage = (negative_frames / total_frames) * 100

    if anticlockwise_percentage > clockwise_percentage:
        dominant_side = ("Anticlockwise Lean")

    elif clockwise_percentage > anticlockwise_percentage:
        dominant_side = ("Clockwise Lean")

    else:
        dominant_side = "Balanced"


    """
    Computes Head Stability
    for a specific bowling phase.

    CONCEPT : Measures how much the head deviates from its average movement path.
    Lower standard deviation -> more stable head movement
    Higher standard deviation -> unstable / highly varying head movement

                            1
    FORMULA :   sigma_x² = --- Σ(x_t - x̄)²
                            n

    where:
    x_t = nose x-coordinate at frame t
    x̄  = mean nose x-coordinate
    """


    # STEP 9 : NOSE X COORDINATES
    nose_x = phase_df["nose_x"]

    # STEP 10 : MEAN HEAD POSITION
    mean_nose_x = nose_x.mean()

    # STEP 11 : DEVIATION FROM MEAN
    deviation = (nose_x - mean_nose_x)

    # STEP 12 : VARIANCE
    variance = np.mean(deviation ** 2)

    # STEP 13 : STANDARD DEVIATION
    stability_std_x = np.sqrt(variance)

    # RETURN
    return {
        "phase": phase_name,
        "signed_mean" : signed_mean,
        "abs_mean" : abs_mean,
        "std_dev" : std_dev,
        "max_abs" : max_abs,
        "dominant_side" : dominant_side,
        "anticlockwise_percentage" : anticlockwise_percentage,
        "clockwise_percentage" : clockwise_percentage,
        # "mean_head_x" : mean_nose_x,
        "head_stability_std_x" : stability_std_x,
    }

def knee_angle_metrics( df: pd.DataFrame, phase_name: str ):
    """
    Computes Knee Angle progression
    for a specific bowling phase.

    CONCEPT : Measures lower-body compression and extension mechanics.
    Lower knee angle -> more compression/flexion
    Higher knee angle -> more extension

    NOTE :
    Since knee angles are already present
    in the dataframe, we directly analyze
    their temporal evolution.
    """

    # STEP 1 : FILTER PHASE
    phase_df = df[df["phase"] == phase_name ].copy()

    if phase_df.empty:
        raise ValueError(f"No rows found for phase: {phase_name}")

    # STEP 2 : DETERMINE FRONT/BACK LEG
    bowling_arm = (phase_df["bowling_arm"].iloc[0].lower())

    # RIGHT ARM BOWLER
    # front leg -> left leg
    # back leg  -> right leg

    if bowling_arm == "right":
        back_knee = (phase_df["right_knee_angle"])

    # LEFT ARM BOWLER
    # front leg -> right leg
    # back leg  -> left leg
    else:
        back_knee = (phase_df["left_knee_angle"])

    # STEP 3 : STORE IN DATAFRAME
    phase_df["back_knee_angle"] = (back_knee)

    # STEP 4 : FRAME-TO-FRAME CHANGE
    phase_df["back_knee_delta"] = (phase_df["back_knee_angle"].diff().fillna(0))

    # RETURN
    return {

        "phase": phase_name,
        # RAW SEQUENCES FOR LLM
        "back_knee_sequence" : phase_df["back_knee_angle"].tolist(),
        "back_knee_delta_sequence" : phase_df["back_knee_delta"].tolist(),

        # AGGREGATED METRICS
        "back_knee_mean" : back_knee.mean(),
        "back_knee_std" : back_knee.std(),
        "back_knee_min" : back_knee.min(),
        "back_knee_max" : back_knee.max()
    }

def delivery_stride_direction_metrics(df: pd.DataFrame, metadata: dict):
    """
    Computes Delivery Stride Direction
    using ONLY:
    - Back Foot Contact frame
    - Front Foot Contact / Release frame

    FORMULA :
    Front Foot = (X_f, Y_f)
    Back Foot  = (X_b, Y_b)
    theta = atan2((X_f - X_b), (Y_f - Y_b))

    Reference:
        vertical direction
    """

    # STEP 1 : EXTRACT METADATA
    bfc_frame = metadata["back_foot_contact_frame"]
    ffc_frame = metadata["release_frame/front_foot_frame"]
    front_foot = metadata["front_foot"]
    back_foot = metadata["back_foot"]

    # STEP 2 : GET BFC ROW
    bfc_row = df[df["frame"] == bfc_frame]

    # STEP 3 : GET FFC ROW
    ffc_row = df[df["frame"] == ffc_frame]

    if bfc_row.empty or ffc_row.empty:
        raise ValueError("Required frames not found.")

    # STEP 4 : BACK FOOT COORDINATES
    # from BFC frame
    X_b = bfc_row[f"{back_foot}_ankle_x"].values[0]
    Y_b = bfc_row[f"{back_foot}_ankle_y"].values[0]

    # STEP 5 : FRONT FOOT COORDINATES
    # from FFC frame
    X_f = ffc_row[f"{front_foot}_ankle_x"].values[0]
    Y_f = ffc_row[f"{front_foot}_ankle_y"].values[0]

    # STEP 6 : STRIDE DIRECTION ANGLE : theta = atan2(Xf - Xb,Yf - Yb)
    theta_rad = np.arctan2((X_f - X_b),(Y_f - Y_b))
    theta_deg = np.degrees(theta_rad)

    # RETURN
    return {
        "bfc_frame" : bfc_frame,
        "ffc_frame" : ffc_frame,
        "stride_direction_angle_deg" : theta_deg
    }

def trunk_lateral_flexion_metrics(df: pd.DataFrame,phase_name: str):
    """
    Computes Trunk Lateral Flexion
    for a specific bowling phase.

    CONCEPT :Measures trunk side-flexion style using shoulder-hip centerline tilt.

    Positive theta -> trunk leaning one side
    Negative theta -> trunk leaning opposite side

    FORMULA :
    mid_shoulder = (Xs, Ys)
    mid_hip      = (Xh, Yh)
    theta        = atan2((Xs - Xh),(Yh - Ys))

    Reference:
        vertical body axis
    """

    # STEP 1 : FILTER PHASE
    phase_df = df[df["phase"] == phase_name].copy()

    if phase_df.empty:
        raise ValueError(f"No rows found for phase: {phase_name}")

    # STEP 2 : MID SHOULDER
    phase_df["mid_shoulder_x"] = (phase_df["left_shoulder_x"] + phase_df["right_shoulder_x"]) / 2
    phase_df["mid_shoulder_y"] = (phase_df["left_shoulder_y"] + phase_df["right_shoulder_y"]) / 2

    # STEP 3 : MID HIP
    phase_df["mid_hip_x"] = (phase_df["left_hip_x"] + phase_df["right_hip_x"]) / 2
    phase_df["mid_hip_y"] = (phase_df["left_hip_y"] + phase_df["right_hip_y"]) / 2

    # STEP 4 : TRUNK FLEXION ANGLE : theta = atan2(Xs - Xh,Yh - Ys)
    theta_rad = np.arctan2((phase_df["mid_shoulder_x"] - phase_df["mid_hip_x"]),(phase_df["mid_hip_y"] - phase_df["mid_shoulder_y"]))
    theta_deg = np.degrees(theta_rad)
    phase_df["trunk_flexion_theta_deg"] = theta_deg

    # STEP 5 : METRICS
    abs_mean = np.abs(theta_deg).mean()
    std_dev = theta_deg.std()

    # RETURN
    return {
        "phase" : phase_name,
        # RAW SEQUENCE FOR LLM :
        "theta_sequence" : theta_deg.tolist(),
        # METRICS :
        "abs_mean" : abs_mean,
        "std_dev" : std_dev
    }

def calculate_bowler_com(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates whole-body Center of Mass (COM)
    using Winter/Dempster anthropometric model.

    Required columns:
    -----------------
    left_shoulder_x, left_shoulder_y
    right_shoulder_x, right_shoulder_y

    left_elbow_x, left_elbow_y
    right_elbow_x, right_elbow_y

    left_wrist_x, left_wrist_y
    right_wrist_x, right_wrist_y

    left_hip_x, left_hip_y
    right_hip_x, right_hip_y

    left_knee_x, left_knee_y
    right_knee_x, right_knee_y

    left_ankle_x, left_ankle_y
    right_ankle_x, right_ankle_y
    """

    # SEGMENT MASSES (Winter anthropometric table) :

    m_trunk = 0.497
    m_thigh = 0.100
    m_leg = 0.0465
    m_upper_arm = 0.028
    m_forearm = 0.016

    # TRUNK COM :

    shoulder_mid_x = (df["left_shoulder_x"] + df["right_shoulder_x"]) / 2
    shoulder_mid_y = (df["left_shoulder_y"] + df["right_shoulder_y"]) / 2

    hip_mid_x = (df["left_hip_x"] + df["right_hip_x"]) / 2
    hip_mid_y = (df["left_hip_y"] + df["right_hip_y"]) / 2

    trunk_com_x = shoulder_mid_x + 0.5 * (hip_mid_x - shoulder_mid_x)
    trunk_com_y = shoulder_mid_y + 0.5 * (hip_mid_y - shoulder_mid_y)

    # LEFT THIGH :
    left_thigh_com_x = df["left_hip_x"] + 0.433 * (df["left_knee_x"] - df["left_hip_x"])
    left_thigh_com_y = df["left_hip_y"] + 0.433 * (df["left_knee_y"] - df["left_hip_y"])

    # RIGHT THIGH :

    right_thigh_com_x = df["right_hip_x"] + 0.433 * (df["right_knee_x"] - df["right_hip_x"])
    right_thigh_com_y = df["right_hip_y"] + 0.433 * (df["right_knee_y"] - df["right_hip_y"])

    # LEFT LEG / SHANK :
    left_leg_com_x = df["left_knee_x"] + 0.433 * (df["left_ankle_x"] - df["left_knee_x"])
    left_leg_com_y = df["left_knee_y"] + 0.433 * (df["left_ankle_y"] - df["left_knee_y"])

    # RIGHT LEG / SHANK :
    right_leg_com_x = df["right_knee_x"] + 0.433 * (df["right_ankle_x"] - df["right_knee_x"])
    right_leg_com_y = df["right_knee_y"] + 0.433 * (df["right_ankle_y"] - df["right_knee_y"])

    # LEFT UPPER ARM :
    left_upper_arm_com_x = df["left_shoulder_x"] + 0.436 * (df["left_elbow_x"] - df["left_shoulder_x"])
    left_upper_arm_com_y = df["left_shoulder_y"] + 0.436 * (df["left_elbow_y"] - df["left_shoulder_y"])

    # RIGHT UPPER ARM :
    right_upper_arm_com_x = df["right_shoulder_x"] + 0.436 * (df["right_elbow_x"] - df["right_shoulder_x"])
    right_upper_arm_com_y = df["right_shoulder_y"] + 0.436 * (df["right_elbow_y"] - df["right_shoulder_y"])

    # LEFT FOREARM :
    left_forearm_com_x = df["left_elbow_x"] + 0.430 * (df["left_wrist_x"] - df["left_elbow_x"])
    left_forearm_com_y = df["left_elbow_y"] + 0.430 * (df["left_wrist_y"] - df["left_elbow_y"])

    # RIGHT FOREARM :
    right_forearm_com_x = df["right_elbow_x"] + 0.430 * (df["right_wrist_x"] - df["right_elbow_x"])
    right_forearm_com_y = df["right_elbow_y"] + 0.430 * (df["right_wrist_y"] - df["right_elbow_y"])

    # TOTAL MASS :

    total_mass = (m_trunk + 2 * m_thigh + 2 * m_leg + 2 * m_upper_arm + 2 * m_forearm)

    # WHOLE BODY COM X :
    com_x = ( m_trunk * trunk_com_x + m_thigh * left_thigh_com_x + m_thigh * right_thigh_com_x + m_leg * left_leg_com_x + m_leg * right_leg_com_x + m_upper_arm * left_upper_arm_com_x + m_upper_arm * right_upper_arm_com_x + m_forearm * left_forearm_com_x + m_forearm * right_forearm_com_x ) / total_mass

    # WHOLE BODY COM Y :
    com_y = (m_trunk * trunk_com_y + m_thigh * left_thigh_com_y + m_thigh * right_thigh_com_y + m_leg * left_leg_com_y + m_leg * right_leg_com_y + m_upper_arm * left_upper_arm_com_y + m_upper_arm * right_upper_arm_com_y + m_forearm * left_forearm_com_y + m_forearm * right_forearm_com_y) / total_mass

    # STORE RESULTS :
    df["com_x"] = com_x
    df["com_y"] = com_y

    return df

def balance_post_delivery_metrics(df: pd.DataFrame, phase_name: str):
    """
    Computes Post-Delivery Balance
    for a specific bowling phase.

    CONCEPT : A bowler is considered balanced if:
    Xmin < COM_x < Xmax
    and
    Ymin < COM_y < Ymax

    where support base is formed by:
    - front ankle
    - back ankle
    """

    # STEP 1 : FILTER PHASE :
    phase_df = df[df["phase"] == phase_name].copy()

    if phase_df.empty:
        raise ValueError(f"No rows found for phase: {phase_name}")

    # STEP 2 : CALCULATE COM :
    phase_df = calculate_bowler_com(phase_df)


    # STEP 3 : DETERMINE FRONT/BACK FOOT :
    bowling_arm = (phase_df["bowling_arm"].iloc[0].lower())

    # RIGHT ARM BOWLER
    if bowling_arm == "right":
        front_foot = "left"
        back_foot = "right"

    # LEFT ARM BOWLER
    else:
        front_foot = "right"
        back_foot = "left"


    # STEP 4 : SUPPORT BASE :

    X_fa = phase_df[f"{front_foot}_ankle_x"]
    Y_fa = phase_df[f"{front_foot}_ankle_y"]

    X_ba = phase_df[f"{back_foot}_ankle_x"]
    Y_ba = phase_df[f"{back_foot}_ankle_y"]

    # STEP 5 : SUPPORT LIMITS :

    Xmin = np.minimum( X_fa, X_ba)
    Xmax = np.maximum( X_fa, X_ba)

    Ymin = np.minimum( Y_fa, Y_ba)
    Ymax = np.maximum( Y_fa, Y_ba)

    # STEP 6 : BALANCE CHECK :
 
    balanced_x = ((phase_df["com_x"] > Xmin) & (phase_df["com_x"] < Xmax))
    balanced_y = ((phase_df["com_y"] > Ymin) & (phase_df["com_y"] < Ymax))

    phase_df["is_balanced"] = (balanced_x & balanced_y)

    # STEP 7 : BALANCE SCORE :

    balance_percentage = (phase_df["is_balanced"].mean()) * 100


    # RETURN
    return {

        "phase" : phase_name,

        # RAW FRAME-WISE DATA :
        "balance_sequence" : phase_df["is_balanced"].tolist(),

        # METRICS
        "balanced_frames" : int(phase_df["is_balanced"].sum()),
        "unbalanced_frames" : int((~phase_df["is_balanced"]).sum()),
        "balance_percentage" : balance_percentage
    }

def bowler_stance_at_backfoot_contact(df: pd.DataFrame, phase_name: str = "Backfoot Phase"):
    """
    Computes bowler stance classification
    using hip orientation during backfoot contact.
    """

    # STEP 1 : FILTER PHASE
    phase_df = df[df["phase"] == phase_name].copy()

    if phase_df.empty:
        raise ValueError(f"No rows found for phase: {phase_name}")

    # STEP 2 : HIP COORDINATES
    xL = phase_df["left_hip_x"]
    yL = phase_df["left_hip_y"]

    xR = phase_df["right_hip_x"]
    yR = phase_df["right_hip_y"]

    # STEP 3 : COMPUTE dx, dy
    dx = np.abs(xR - xL)
    dy = np.abs(yR - yL)

    # AVOID DIVISION BY ZERO
    dy = np.where(dy == 0, 1e-6, dy)

    # STEP 4 : COMPUTE theta
    theta_rad = np.arctan(dx / dy)

    theta_deg = np.degrees(theta_rad)

    phase_df["stance_theta_deg"] = theta_deg

    # STEP 5 : AVERAGE ANGLE
    avg_theta = theta_deg.mean()
    total_frames = len(theta_deg)

    # STEP 6 : CLASSIFICATION
    if 0 <= avg_theta < 25:
        stance = "Side-on"

    elif 25 <= avg_theta < 60:
        stance = "Semi-side-on"

    elif 60 <= avg_theta <= 90:
        stance = "Front-on"

    else:
        stance = "Mixed Position"

    # STEP 7 : RETURN
    return {
        "phase": phase_name,
        "total_frames": total_frames,
        "average_theta_deg": avg_theta,
        "bowler_stance": stance
    }

def front_foot_knee_bracing(df: pd.DataFrame, bowling_arm: str, phase_name: str = "Frontfoot Phase"):
    """
    Checks whether front foot knee is braced
    (near straight / extended).
    """

    # STEP 1 : FILTER PHASE
    phase_df = df[df["phase"] == phase_name].copy()

    if phase_df.empty:
        raise ValueError(f"No rows found for phase: {phase_name}")

    # STEP 2 : DETERMINE FRONT FOOT
    bowling_arm = bowling_arm.lower()

    if bowling_arm == "right":
        front_knee_col = "left_knee_angle"

    elif bowling_arm == "left":
        front_knee_col = "right_knee_angle"

    else:
        raise ValueError("bowling_arm must be 'right' or 'left'")

    # STEP 3 : FETCH KNEE ANGLE
    knee_angle = phase_df[front_knee_col]

    phase_df["front_foot_knee_angle"] = knee_angle

    # STEP 4 : METRICS
    avg_angle = knee_angle.mean()
    std_angle = knee_angle.std()
    min_angle = knee_angle.min()
    max_angle = knee_angle.max()
    total_frames = len(knee_angle)

    # STEP 5 : CLASSIFICATION
    if avg_angle > 130:
        knee_status = "Braced / Straight Knee"
    else:
        knee_status = "Bent / Collapsing Knee"

    # STEP 6 : RETURN
    return {
        "phase": phase_name,
        "bowling_arm": bowling_arm,
        "front_foot": "left" if bowling_arm == "right" else "right",
        "total_frames": total_frames,

        # Raw evidence for LLM
        "knee_angle_sequence": knee_angle.tolist(),

        # Statistics
        "mean_knee_angle_deg": avg_angle,
        "std_knee_angle_deg": std_angle,
        "min_knee_angle_deg": min_angle,
        "max_knee_angle_deg": max_angle,

        # Optional interpretation
        "knee_status": knee_status
    }

def release_bowling_arm_elbow_angle(df: pd.DataFrame, bowling_arm: str, phase_name: str = "Frontfoot Phase"):
    """
    Checks whether bowling arm elbow
    is straight / extended at release.
    """

    # STEP 1 : FILTER PHASE
    phase_df = df[df["phase"] == phase_name].copy()

    if phase_df.empty:
        raise ValueError(f"No rows found for phase: {phase_name}")

    # STEP 2 : DETERMINE BOWLING ARM ELBOW COLUMN
    bowling_arm = bowling_arm.lower()

    if bowling_arm == "right":
        elbow_col = "right_elbow_angle"

    elif bowling_arm == "left":
        elbow_col = "left_elbow_angle"

    else:
        raise ValueError("bowling_arm must be 'right' or 'left'")

    # STEP 3 : FETCH ELBOW ANGLE
    elbow_angle = phase_df[elbow_col]

    phase_df["release_bowling_arm_elbow_angle"] = elbow_angle

    # STEP 4 : METRICS
    avg_angle = elbow_angle.mean()
    total_frames = len(elbow_angle)

    # STEP 5 : CLASSIFICATION
    if avg_angle > 130:
        elbow_status = "Straight / Extended Arm"

    else:
        elbow_status = "Bent Elbow"

    # STEP 6 : RETURN
    return {
        "phase": phase_name,
        "bowling_arm": bowling_arm,
        "total_frames": total_frames,
        "average_elbow_angle_deg": avg_angle,
        "elbow_status": elbow_status
    }

def wrist_position_after_follow_through(df: pd.DataFrame, bowling_arm):
    """
    Evaluates bowling-arm follow-through.

    Level 1:
        Wrist below front knee
        -> Excellent Follow Through

    Level 2:
        Wrist below midpoint(front hip, front knee)
        -> Moderate Follow Through

    Level 3:
        Wrist above midpoint(front hip, front knee)
        -> Limited Follow Through
    """

    phase_df = df[df["phase"] == "Follow Through"].copy()

    if phase_df.empty:
        raise ValueError("No Follow Through frames found")

    bowling_arm = bowling_arm.lower()

    if bowling_arm == "right":
        wrist_col = "right_wrist_y"
        front_knee_col = "left_knee_y"
        front_hip_col = "left_hip_y"

    elif bowling_arm == "left":
        wrist_col = "left_wrist_y"
        front_knee_col = "right_knee_y"
        front_hip_col = "right_hip_y"

    else:
        raise ValueError("bowling_arm must be 'right' or 'left'")

    # LEVEL 1 : Wrist below front knee ;

    for _, row in phase_df.iterrows():

        wrist_y = row[wrist_col]
        knee_y = row[front_knee_col]

        if wrist_y > knee_y:
            return {"followthrough_status": "Good Follow Through"}

    # LEVEL 2 : Wrist below hip-knee midpoint :

    for _, row in phase_df.iterrows():

        wrist_y = row[wrist_col]
        knee_y = row[front_knee_col]
        hip_y = row[front_hip_col]
        midpoint_y = (knee_y + hip_y) / 2

        if wrist_y > midpoint_y:
            return {"followthrough_status": "Moderate Follow Through"}

    # LEVEL 3 : Limited follow-through :

    return {"followthrough_status": "Limited Follow Through"}

def generate_biomechanics_report(df: pd.DataFrame, metadata: dict ):
    """
    Runs all biomechanics attribute functions
    phase-wise and returns one structured report.
    """

    gather_available = (
        metadata["phases"][0]["start_frame"] != -1 and
        metadata["phases"][0]["end_frame"] != -1
    )

    biomechanics_report = {

        "Bowling Arm": df["bowling_arm"].iloc[0],

        # GATHER PHASE : 
        "Gather Phase": (
            {
                "Hip direction as the bowler loads up": hip_direction_as_bowler_loadsup(df, "Gather Phase"),
                "Hip-Shoulder Alignment": hip_shoulder_alignment_metrics(df, "Gather Phase"),
                "Head Position & Stability": head_position_stability_metrics(df, "Gather Phase"),
                "Shoulder Tilt Progression": shoulder_tilt_progression_metrics(df)
            }
            if gather_available
            else {"status": "Not enough data for Gather Phase"}

        ),

        # BACKFOOT PHASE :

        "Backfoot Phase": {
            "bowler stance" : bowler_stance_at_backfoot_contact(df, "Backfoot Phase"),
            "Hip direction as the bowler loads up" : hip_direction_as_bowler_loadsup( df, "Backfoot Phase"),
            "Knee Angle" : knee_angle_metrics( df, "Backfoot Phase" )
        },

        # DELIVERY STRIDE :

        "Delivery Stride": {

            "Delivery Stride Direction" : delivery_stride_direction_metrics(df, metadata),
            "Hip-Shoulder Alignment" : hip_shoulder_alignment_metrics(df, "Delivery Stride"),
            "Head Position & Stability" : head_position_stability_metrics(df, "Delivery Stride"),
            "Trunk Lateral Flexion" : trunk_lateral_flexion_metrics(df, "Delivery Stride")
        },

        # FRONTFOOT PHASE :

        "Frontfoot Phase": {
            "front foot knee bracing" : front_foot_knee_bracing(df, df["bowling_arm"].iloc[0]),
            "Release bowling arm elbow angle" : release_bowling_arm_elbow_angle(df, bowling_arm=df["bowling_arm"].iloc[0]),
            "Hip-Shoulder Alignment" : hip_shoulder_alignment_metrics(df, "Frontfoot Phase"),
            "Trunk Lateral Flexion" : trunk_lateral_flexion_metrics(df, "Frontfoot Phase")
        },

        # FOLLOW THROUGH :

        "Follow Through": {
            "wrist position after follow through" : wrist_position_after_follow_through(df, bowling_arm=df["bowling_arm"].iloc[0]),
            "Balance Post-Delivery" : balance_post_delivery_metrics(df, "Follow Through"),
            "Trunk Lateral Flexion" : trunk_lateral_flexion_metrics( df, "Follow Through")
        }
    }

    return biomechanics_report