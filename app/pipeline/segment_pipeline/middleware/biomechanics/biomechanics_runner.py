import pandas as pd, logging
from app.pipeline.segment_pipeline.middleware.biomechanics.fetch import fetch_keypoint_data
from app.pipeline.segment_pipeline.middleware.biomechanics.frames import find_phase_frames
from app.pipeline.segment_pipeline.middleware.biomechanics.attributes import generate_biomechanics_report
from app.pipeline.segment_pipeline.agents.biomechanics_agent import generate_biomechanics_analysis
from app.core.logging_setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def run_biomechanics(df: pd.DataFrame, release_frame, df_bowler_keypoints_for_bowling_amr) -> pd.DataFrame:

    # Step 1 → fetching keypoint from the file
    print("Fetching biomechanics data...\n")
    df = fetch_keypoint_data(df, release_frame, df_bowler_keypoints_for_bowling_amr)
    print("✅ Data Loaded Successfully")

    print("===========================================================================")
    print(df)
    print("\n")
    print(df["right_wrist_y"])
    print("===========================================================================")


    # STEP 2 → Dividing the dataframe phase wise & get dataframe + metadata
    print("Dividing the frames into the phases...\n")
    # updated_df, metadata = find_phase_frames(df, release_frame)
    try:
        updated_df, metadata = find_phase_frames(df, release_frame)

    except ValueError as e:
        logger.error(f"{e}")
        updated_df = None
        metadata = None

    print("=================================================")
    print("metadata : ")
    print(metadata)
    print("=================================================")
    print("=================================================")
    print("updated_df : ")
    print(updated_df)
    print("=================================================")

    print("✅ DataFrame and metadata created successfully")

    # STEP 3 → GENERATE ATTRIBUTES
    print("Generating biomechanics attributes report...\n")
    report = generate_biomechanics_report(updated_df, metadata)

    return report, metadata