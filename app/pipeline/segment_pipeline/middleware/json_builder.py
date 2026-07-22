def convert_to_python_type(value):
    import numpy as np
    
    if isinstance(value, (np.integer,)):
        return int(value)
    elif isinstance(value, (np.floating,)):
        return float(value)
    elif isinstance(value, (np.ndarray,)):
        return value.tolist()
    elif isinstance(value, dict):
        return {k: convert_to_python_type(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [convert_to_python_type(v) for v in value]
    return value


def build_json(df, stats, biomech_report):
    deliveries = []

    for _, row in df.iterrows():
        delivery = {
            "metadata": {
                "bowler_arm": str(row["bowler_arm"]),
                "speed_kmph": float(row["speed"]),
            },
            "physics": {
                "release_point": [
                    float(row["release_x"]),
                    float(row["release_y"])
                ],
                "bounce_point": [
                    float(row["bounce_x"]),
                    float(row["bounce_y"])
                ],
                # "impact_point": [
                #     float(row["impact_x"]),
                #     float(row["impact_y"])
                # ],
                "air_swing": float(row["air_swing"]),
                # "seam_movement": float(row["seam_movement"]),
                # "total_movement": float(row["total_movement"]),
                "time_to_batsman": float(row["time_to_batsman"]),
            },
            "features": {
                "length": str(row["length"]),
                "line": str(row["line"]),
                "swing_type": str(row["swing_type"]),
                "pace_type": str(row["pace_type"]),
            }
        }

        deliveries.append(delivery)

    stats_clean = {}
    for k, v in stats.items():
        stats_clean[k] = convert_to_python_type(v)

    final_data = {
        "deliveries": deliveries,
        "stats": stats_clean,
        "biomechanics": biomech_report
    }

    return final_data