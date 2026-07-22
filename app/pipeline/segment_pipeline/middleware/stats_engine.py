def calculate_stats(df):
    stats = {}

    stats["total_deliveries"] = len(df)
    stats["avg_speed"] = df["speed"].mean()
    stats["avg_swing"] = df["air_swing"].mean()

    stats["yorker_count"] = (df["length"] == "yorker").sum()
    stats["full_count"] = (df["length"] == "full").sum()
    stats["good_length_count"] = (df["length"] == "good_length").sum()
    stats["short_count"] = (df["length"] == "short").sum()

    return stats