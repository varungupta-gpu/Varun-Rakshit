import pandas as pd
import logging

logger = logging.getLogger(__name__)

def extract_dqi(df):

    df_new = pd.DataFrame()

    try:
        df_new["impact_x"] = df["meta.impact_coord.x"]

    except Exception as e:
        logger.error(f"ERROR while extracting impact_x.\n Reason: {str(e)}")


    df_new["impact_y"] = df["meta.impact_coord.y"]
    df_new["impact_frame"] = df["meta.impact_coord.frame"]

    return df_new


def extract_delivery(df):
    df_new = pd.DataFrame()

    df_new["release_x"] = df["release.x"]
    df_new["release_y"] = df["release.y"]
    df_new["release_frame"] = df["release.frame"]

    df_new["bounce_x"] = df["bounce.x"]
    df_new["bounce_y"] = df["bounce.y"]
    df_new["bounce_frame"] = df["bounce.frame"]

    df_new["speed"] = df["speed"]
    df_new["time_to_batsman"] = df["physics.flight_time_s"]
    df_new["distance"] = df["physics.straight_line_distance_3d_m"]

    return df_new


def extract_final(df):
    df_new = pd.DataFrame()

    df_new["bowler_arm"] = df["bowling_arm"]
    df_new["ball_x"] = df["x_3d"]
    df_new["ball_y"] = df["y_3d"]
    df_new["ball_z"] = df["z_3d"]
    df_new["frame"] = df["frame"]
    # print(df[["bowling_arm"]].head())
    # print(df["bowling_arm"].value_counts(dropna=False))

    return df_new


# def extract_all(df_dqi, df_final, df_delivery):

def extract_all(df_final, df_delivery):
    # dqi = extract_dqi(df_dqi)
    final = extract_final(df_final)
    delivery = extract_delivery(df_delivery)

    return final, delivery
    # return dqi, final, delivery