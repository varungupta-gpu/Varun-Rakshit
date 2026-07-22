def calculate_physics(df):
    df["air_swing"] = df["bounce_x"] - df["release_x"]
    # df["seam_movement"] = df["impact_x"] - df["bounce_x"]
    # df["total_movement"] = df["impact_x"] - df["release_x"]

    df["avg_velocity"] = df["distance"] / df["time_to_batsman"]

    return df