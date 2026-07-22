from app.pipeline.segment_pipeline.middleware.data_loader import load_all
from app.pipeline.segment_pipeline.middleware.data_extractor import extract_all
from app.pipeline.segment_pipeline.middleware.data_merger import merge_data
from app.pipeline.segment_pipeline.middleware.data_validator import validate_data
from app.pipeline.segment_pipeline.middleware.physics_engine import calculate_physics
from app.pipeline.segment_pipeline.middleware.feature_engine import generate_features
from app.pipeline.segment_pipeline.middleware.stats_engine import calculate_stats
from app.pipeline.segment_pipeline.middleware.json_builder import build_json
# from app.pipeline.segment_pipeline.middleware.biomechanics_analyzer import BiomechanicsAnalyzer
from app.pipeline.segment_pipeline.middleware.biomechanics.biomechanics_runner import run_biomechanics
# Lazy import to avoid Langfuse authentication issues during module load
import pandas as pd
import logging
from pathlib import Path

def run_pipeline(cv_data, dqi_report, final_combined_json_path, bowler_keypoint_df, release_frame, local_bowler_keypoints_csv_path_for_bowling_arm):

    print("Loading data...")
    df_dqi, df_final, df_delivery, df_bowler_keypoints_for_bowling_amr = load_all(cv_data, dqi_report, final_combined_json_path, local_bowler_keypoints_csv_path_for_bowling_arm)

    print("Extracting data...")
    # dqi, final, delivery = extract_all(df_dqi, df_final, df_delivery)
    final, delivery = extract_all(df_final, df_delivery)

    print("Merging data...")
    # master = merge_data(dqi, final, delivery)
    master = merge_data(final, delivery)

    print("Validating data...")
    # master = validate_data(master)

    print("Calculating physics...")
    master = calculate_physics(master)

    print("Generating features...")
    master = generate_features(master)

    print("Calculating stats...")
    stats = calculate_stats(master)

    print("Running biomechanics analysis...")
    bowler_keypoint_df = df_bowler_keypoints_for_bowling_amr
    biomech_report, metadata = run_biomechanics(bowler_keypoint_df, release_frame, df_bowler_keypoints_for_bowling_amr)

    print("Building JSON...")
    json_data = build_json(master, stats, biomech_report)

    print("Pipeline completed!")

    # Adding metadata to the biomechanics report, which we can save in DB for player level analysis
    biomech_report["metadata"] = metadata

    return json_data, biomech_report

# pipeline for batter that generates biomechanics and stats
logger = logging.getLogger(__name__)

# Default model path: middleware/batting/models/phase_classifier.pkl
DEFAULT_BATTING_MODEL_PATH = Path(__file__).resolve().parent / "batting" / "models" / "phase_classifier.pkl"


def run_pipeline_batsman(batsman_keypoints_df: pd.DataFrame, model_path: str = None) -> tuple:
    """
    Main batting analysis pipeline - ALL IN-MEMORY (no file I/O).
    
    Args:
        batsman_keypoints_df: DataFrame with batsman keypoints (COCO format)
                               Required columns: frame, nose_x, nose_y, left_shoulder_x, 
                               right_shoulder_x, left_elbow_x, right_elbow_x, left_wrist_x, 
                               right_wrist_x, left_hip_x, right_hip_x, left_knee_x, right_knee_x,
                               left_ankle_x, right_ankle_x (and corresponding _y columns)
        model_path: Path to phase classification model (.pkl file)
                    If None, uses default: middleware/batting/models/phase_classifier.pkl
    
    Returns:
        tuple: (batting_report dict, metadata dict)
    
    Raises:
        ValueError: If keypoints_df is None or empty
        ValueError: If required keypoint columns are missing
    
    Flow:
        keypoints_df (variable)
        ↓
        predict_phases() 
        ↓
        downswing_predictions (variable in memory - NOT saved to disk)
        ↓
        infer_batting_phases()
        ↓
        batting_phases_df (variable in memory - NOT saved to disk)
        ↓
        compute_features()
        ↓
        features_dict (variable in memory - NOT saved to disk)
        ↓
        calculate_statistics()
        ↓
        statistics_dict (variable in memory - NOT saved to disk)
        ↓
        batting_report (returned to main.py)
    """
    
    # ================================================================
    # VALIDATION: Check keypoints DataFrame
    # ================================================================
    
    if batsman_keypoints_df is None:
        raise ValueError("batsman_keypoints_df cannot be None. Please provide keypoints DataFrame.")
    
    if batsman_keypoints_df.empty:
        raise ValueError("batsman_keypoints_df is empty. Please provide valid keypoints data.")
    
    if not isinstance(batsman_keypoints_df, pd.DataFrame):
        raise TypeError(f"batsman_keypoints_df must be a pandas DataFrame, got {type(batsman_keypoints_df)}")
    
    # Check for required columns
    required_keypoints = [
        'nose', 'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
        'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
        'left_knee', 'right_knee', 'left_ankle', 'right_ankle'
    ]
    
    missing_keypoints = []
    for kp in required_keypoints:
        if f'{kp}_x' not in batsman_keypoints_df.columns or f'{kp}_y' not in batsman_keypoints_df.columns:
            missing_keypoints.append(kp)
    
    if missing_keypoints:
        raise ValueError(
            f"Missing required keypoint columns: {missing_keypoints}. "
            f"Available columns: {list(batsman_keypoints_df.columns)[:10]}..."
        )
    
    # Check for frame column
    if 'frame' not in batsman_keypoints_df.columns and 'frame_no' not in batsman_keypoints_df.columns:
        raise ValueError("keypoints_df must have 'frame' or 'frame_no' column")
    
    logger.info(f"✓ Keypoints validated: {len(batsman_keypoints_df)} frames, {len(batsman_keypoints_df.columns)} columns")
    
    # ================================================================
    # Set default model path if not provided
    # ================================================================
    
    if model_path is None:
        model_path = str(DEFAULT_BATTING_MODEL_PATH)
        logger.info(f"Using default model: {model_path}")
    
    if not Path(model_path).exists():
        raise FileNotFoundError(
            f"Phase classification model not found: {model_path}. "
            f"Expected model location: middleware/batting/models/phase_classifier.pkl"
        )
    
    # ================================================================
    # PIPELINE EXECUTION
    # ================================================================
    
    try:
        logger.info("Starting batting analysis pipeline (in-memory mode)...")
        
        # ================================================================
        # STEP 1: PREDICT DOWNSWING PHASES
        # ================================================================
        logger.info("Step 1: Predicting downswing phases...")
        from app.pipeline.segment_pipeline.middleware.batting.phase_classification.predict_phases import predict_downswing_phases
        
        # Variable in memory - NOT saved to file
        downswing_predictions = predict_downswing_phases(
            keypoints_df=batsman_keypoints_df,
            model_path=model_path
        )
        logger.info(f"✅ Downswing predictions: {len(downswing_predictions)} frames (in-memory variable)")
        
        # ================================================================
        # STEP 2: INFER BATTING PHASES FROM DOWNSWING
        # ================================================================
        logger.info("Step 2: Inferring batting phases from downswing...")
        from app.pipeline.segment_pipeline.middleware.batting.phase_inference.infer_batting_phases import infer_phases_from_downswing
        
        # Variable in memory - NOT saved to file
        batting_phases_df = infer_phases_from_downswing(
            keypoints_df=batsman_keypoints_df,
            downswing_predictions=downswing_predictions  # Pass variable directly
        )
        logger.info(f"✅ Batting phases inferred: {len(batting_phases_df)} segments (in-memory variable)")
        
        # ================================================================
        # STEP 3: COMPUTE BIOMECHANICS FEATURES
        # ================================================================
        logger.info("Step 3: Computing biomechanics features...")
        from app.pipeline.segment_pipeline.middleware.batting.biomechanics.compute_features import compute_batting_features
        
        # Variable in memory - NOT saved to file
        features_dict = compute_batting_features(
            phases_df=batting_phases_df,  # Pass variable directly
            keypoints_df=batsman_keypoints_df
        )
        logger.info("✅ Biomechanics features computed (in-memory dict)")
        
        # ================================================================
        # STEP 4: CALCULATE STATISTICS
        # ================================================================
        logger.info("Step 4: Calculating phase-wise statistics...")
        from app.pipeline.segment_pipeline.middleware.batting.biomechanics.calculate_statistics import calculate_phase_statistics
        
        # Variable in memory - NOT saved to file
        statistics_dict = calculate_phase_statistics(
            features_dict=features_dict  # Pass variable directly
        )
        logger.info("✅ Statistics calculated (in-memory dict)")
        
        # ================================================================
        # STEP 5: BUILD BATTING REPORT (No LLM - you'll add later)
        # ================================================================
        logger.info("Step 5: Building batting report...")
        
        batting_report = {
            "biomechanics_features": features_dict,  # Used by batting_agent
            "biomechanics_statistics": statistics_dict,  # Used by batting_agent
            "batting_phases": batting_phases_df.to_dict('records') if not batting_phases_df.empty else [],
            "downswing_predictions": downswing_predictions.to_dict('records') if isinstance(downswing_predictions, pd.DataFrame) else downswing_predictions,
            "metadata": {
                "total_frames": len(batsman_keypoints_df),
                "phases_detected": len(batting_phases_df) if not batting_phases_df.empty else 0,
                "model_path": model_path
            }
        }
        
        metadata = {
            "total_keypoint_frames": len(batsman_keypoints_df),
            "phases_detected": len(batting_phases_df) if not batting_phases_df.empty else 0,
            "model_used": model_path,
            "pipeline_version": "1.0",
            "file_io_used": False  # Confirms no file I/O
        }
        
        logger.info("✅ Batting analysis pipeline complete (all in-memory)")
        return batting_report, metadata
        
    except Exception as e:
        logger.exception(f"❌ Batting analysis pipeline failed: {e}")
        raise 
