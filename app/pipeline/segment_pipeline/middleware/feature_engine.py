def classify_length(y):
    if y < 900:
        return "yorker"
    elif y < 1000:
        return "full"
    elif y < 1150:
        return "good_length"
    else:
        return "short"


def classify_line(x):
    if x < 500:
        return "leg_stump"
    elif x < 650:
        return "middle_stump"
    else:
        return "off_stump"


def classify_swing(swing):
    if swing > 20:
        return "outswing"
    elif swing < -20:
        return "inswing"
    else:
        return "straight"


def classify_pace(speed):
    if speed > 140:
        return "fast"
    elif speed > 130:
        return "medium_fast"
    else:
        return "medium"


def generate_features(df):
    df["length"] = df["bounce_y"].apply(classify_length)
    df["line"] = df["bounce_x"].apply(classify_line)
    df["swing_type"] = df["air_swing"].apply(classify_swing)
    df["pace_type"] = df["speed"].apply(classify_pace)

    return df