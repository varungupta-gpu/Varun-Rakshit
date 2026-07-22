import pandas as pd

def load_all(cv_data, dqi_report, final_combined_json_path=None, local_bowler_keypoints_csv_path_for_bowling_arm=None):
    
    # Load DQI from API data
    df_dqi = pd.json_normalize(dqi_report)

    # Load delivery from CV data
    df_delivery = pd.json_normalize(cv_data)

    # Load FINAL CSV
    df_final = pd.read_csv(final_combined_json_path)

    # Load BOWLER KEYPOINTS
    df_bowler_keypoints_for_bowling_amr = pd.read_csv(local_bowler_keypoints_csv_path_for_bowling_arm)

    return df_dqi, df_final, df_delivery, df_bowler_keypoints_for_bowling_amr
