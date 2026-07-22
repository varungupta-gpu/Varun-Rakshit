import pandas as pd

def get_bowling_wrist_column(bowling_arm: str):
    """
    Returns wrist and shoulder column names based on bowling arm.
    """

    bowling_arm = bowling_arm.lower().strip()

    if bowling_arm == "right":
        wrist_y = "right_wrist_y"
        shoulder_y = "right_shoulder_y"

    elif bowling_arm == "left":
        wrist_y = "left_wrist_y"
        shoulder_y = "left_shoulder_y"

    else:
        raise ValueError("bowling_arm must be either 'left' or 'right'")

    return wrist_y, shoulder_y

def find_phase_frames(df: pd.DataFrame, release_frame):
    """
    Finds:
    1. Gather Start Frame
    2. Back Foot Contact Frame (BFC)
    3. Release Frame

    Logic:
    ------------------------------------------------
    Release Frame:
        frame where is_actual_release == 1

    Back Foot Contact:
        from start -> release frame,
        frame having MAX bowling wrist y-coordinate

    Gather Start:
        before BFC,
        first frame where:
            wrist_y < shoulder_y
    ------------------------------------------------
    """

    release_rows = df[df["frame"] == release_frame]


    # Get bowling arm :
    bowling_arm = str(release_rows.iloc[0]["bowling_arm"]).lower().strip()
    wrist_y_col, shoulder_y_col = get_bowling_wrist_column(bowling_arm)


    # Data till release frame :
    pre_release_df = df[df["frame"] <= release_frame].copy()

    # PHASE AVAILABILITY FLAGS
    gather_available = True


    # Back Foot Contact Frame :
    # MAX wrist_y before release
    bfc_idx = pre_release_df[wrist_y_col].idxmax()
    bfc_frame = int(pre_release_df.loc[bfc_idx, "frame"])

    print("=========================================================================================")
    print("=========================================================================================")
    print("bfc_frame :")
    print(bfc_frame)
    print("=========================================================================================")
    print("=========================================================================================")


    # Frames before BFC :
    before_bfc_df = pre_release_df[pre_release_df["frame"] < bfc_frame].copy()


    # Gather Start Frame :
    # wrist_y < shoulder_y
    gather_candidates = before_bfc_df[
        before_bfc_df[wrist_y_col] < before_bfc_df[shoulder_y_col]
    ]

    if gather_candidates.empty:
        gather_available = False
        gather_start_frame = None

    else:

        gather_start_frame = int(gather_candidates.iloc[0]["frame"])

    # CREATE PHASE COLUMN

    df["phase"] = ""

    # # RUN-UP :
    # df.loc[df["frame"] < gather_start_frame, "phase"] = "Run-up Phase"

    # # GATHER PHASE :
    # df.loc[(df["frame"] >= gather_start_frame) & (df["frame"] < bfc_frame),"phase"] = "Gather Phase"


    # RUN-UP & GATHER PHASE
    if gather_available:
        # RUN-UP :
        df.loc[df["frame"] < gather_start_frame,"phase"] = "Run-up Phase"

        # GATHER PHASE :
        df.loc[(df["frame"] >= gather_start_frame) & (df["frame"] < bfc_frame), "phase"] = "Gather Phase"


    # DELIVERY STRIDE :
    df.loc[(df["frame"] >= bfc_frame) & (df["frame"] <= release_frame), "phase"] = "Delivery Stride"

    # FOLLOW THROUGH :
    df.loc[df["frame"] > release_frame, "phase"] = "Follow Through"

    # FRONT FOOT / BACK FOOT PHASE LABELS
    # BACKFOOT PHASE :
    backfoot_start = bfc_frame - 6
    backfoot_end = bfc_frame + 0

    df.loc[(df["frame"] >= backfoot_start) & (df["frame"] <= backfoot_end),"phase"] = "Backfoot Phase"


    # FRONTFOOT PHASE :
    frontfoot_start = release_frame -1
    frontfoot_end = release_frame + 3

    df.loc[(df["frame"] >= frontfoot_start) & (df["frame"] <= frontfoot_end),"phase"] = "Frontfoot Phase"

    # FRONT FOOT / BACK FOOT :

    if bowling_arm.lower() == "right":
        front_foot = "left"
        back_foot = "right"

    else:
        front_foot = "right"
        back_foot = "left"


    # Gather Phase metadata

    if gather_available:
        gather_metadata_start = gather_start_frame
        gather_metadata_end = backfoot_start - 1

    else:
        gather_metadata_start = -1
        gather_metadata_end = -1

    # METADATA

    metadata = {
        "gather_start_frame": gather_start_frame,
        "back_foot_contact_frame": bfc_frame,
        "release_frame/front_foot_frame": release_frame,
        "bowling_arm": bowling_arm,
        "front_foot": front_foot,
        "back_foot": back_foot,

        "phases": [
            # {
            #     "phase": "Gather Phase",
            #     "start_frame": gather_start_frame,
            #     "end_frame": backfoot_start-1
            # },
            {
                "phase": "Gather Phase",
                "start_frame": gather_metadata_start,
                "end_frame": gather_metadata_end
            },
            {
                "phase": "Backfoot Phase",
                "start_frame": backfoot_start,
                "end_frame": backfoot_end
            },
            {
                "phase": "Delivery Stride",
                "start_frame": bfc_frame+1,
                "end_frame": release_frame-2
            },
            {
                "phase": "Frontfoot Phase",
                "start_frame": frontfoot_start,
                "end_frame": frontfoot_end
            },
            {
                "phase": "Follow Through",
                "start_frame": release_frame + 4,
                "end_frame": int(df["frame"].max())
            }
        ]
    }


    delivery_start = bfc_frame + 1
    delivery_end = release_frame - 2
    followthrough_start = release_frame + 4

    if gather_available:
        valid = (
                gather_metadata_start <= gather_metadata_end <
                backfoot_start <= backfoot_end <
                delivery_start <= delivery_end <
                frontfoot_start <= frontfoot_end <
                followthrough_start
            )

    else:
        valid = (
            backfoot_start <= backfoot_end <
            delivery_start <= delivery_end <
            frontfoot_start <= frontfoot_end <
            followthrough_start
        )

    if not valid:
        raise ValueError("Invalid phase ordering. CSV data is inconsistent.")


    # CLEANUP COLUMNS :
    # Remove tracker_id column
    if "tracker_id" in df.columns:
        df.drop(columns=["tracker_id"], inplace=True)

    # Fill complete bowling_arm column :
    df["bowling_arm"] = bowling_arm


    return df, metadata