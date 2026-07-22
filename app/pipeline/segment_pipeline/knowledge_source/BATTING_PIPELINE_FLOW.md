# Batsman Analysis Pipeline Flow

## Overview
The batsman analysis pipeline processes batsman keypoints data to generate biomechanics analysis and LLM-based batting style classification. The pipeline is designed to be entirely in-memory except for the final LLM output.

## Pipeline Flow

### 1. Data Fetching (main.py)
```
setup_environment_for_batsman_csv(request)
↓
Fetches segment attributes from Video API
↓
Extracts batter_pose_file_path from API response
↓
Downloads CSV from GCS
↓
Loads into pandas DataFrame (batsman_keypoints_df)
```

### 2. Phase Classification Pipeline (middleware/pipeline.py)
```
run_pipeline_batsman(batsman_keypoints_df)
↓
Step 1: Predict Downswing Phases
  - predict_downswing_phases(keypoints_df)
  - Returns: downswing_predictions (DataFrame, in-memory)
↓
Step 2: Infer Batting Phases
  - infer_batting_phases(keypoints_df, downswing_predictions)
  - Returns: batting_phases_df (DataFrame, in-memory)
↓
Step 3: Compute Biomechanics Features
  - compute_batting_features(phases_df, keypoints_df)
  - Returns: features_dict (dict, in-memory)
↓
Step 4: Calculate Statistics
  - calculate_phase_statistics(features_dict)
  - Returns: statistics_dict (dict, in-memory)
↓
Returns: (batting_report dict, metadata dict)
```

### 3. LLM Analysis (agents/batting_agent.py)
```
generate_llm_analysis(biomech_features_dict, statistics_dict, output_dir)
↓
Loads documentation files from knowledge_source:
  - README.md (Features Reference)
  - TEMP.md (Analysis Framework)
↓
Constructs prompt with:
  - Biomechanical features (JSON)
  - Statistics (JSON)
  - Documentation (markdown)
↓
Calls Gemini API (gemini-3.1-flash-lite)
↓
Parses LLM response
↓
Saves final output to disk: style_analysis.json (ONLY disk write)
↓
Returns: Success status (boolean)
```

## Data Flow Summary

**Input:**
- `BallSegmentAnalysisRequest` (contains api_base_url, bearer_access_token, video_id, segment_id)

**Processing (All In-Memory):**
1. Batsman keypoints DataFrame
2. Downswing predictions DataFrame
3. Batting phases DataFrame
4. Biomechanics features dictionary
5. Statistics dictionary

**Output (Saved to Disk):**
- `style_analysis.json` - Final LLM batting style analysis

## Key Features

- **In-Memory Processing**: All intermediate data stays in memory (no file I/O)
- **Error Handling**: Each step wrapped in try-except with proper logging
- **Model Loading**: Phase classification model loaded from `middleware/batting/models/`
- **Documentation**: LLM prompt uses knowledge from `segment_pipeline/knowledge_source/`
- **API Integration**: Uses VideoApiClient for data fetching and Gemini API for analysis

## File Locations

- **Pipeline**: `app/pipeline/segment_pipeline/middleware/pipeline.py` (run_pipeline_batsman)
- **LLM Agent**: `app/pipeline/segment_pipeline/agents/batting_agent.py` (generate_llm_analysis)
- **Setup Function**: `main.py` (setup_environment_for_batsman_csv)
- **Knowledge Source**: `app/pipeline/segment_pipeline/knowledge_source/` (README.md, TEMP.md)
- **Models**: `app/pipeline/segment_pipeline/middleware/batting/models/` (phase_classifier.pkl)

## Usage Example

```python
# In main.py
batsman_keypoints_df = setup_environment_for_batsman_csv(request)
batting_report, batting_metadata = run_pipeline_batsman(batsman_keypoints_df)
batting_llm_success = generate_llm_analysis(
    biomech_features_dict=batting_report["biomechanics_features"],
    statistics_dict=batting_report["biomechanics_statistics"],
    output_dir=batting_llm_output_dir
)
```
