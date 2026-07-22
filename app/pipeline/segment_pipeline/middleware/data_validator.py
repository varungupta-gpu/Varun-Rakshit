def validate_data(df):
    df = df.dropna()

    df = df[df["speed"] > 0]
    df = df[df["time_to_batsman"] > 0]
    df = df[df["bounce_frame"] > df["release_frame"]]
    df = df[df["impact_frame"] > df["bounce_frame"]]

    return df