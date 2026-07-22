def build_physio_query(data):
    """
    Builds a domain-aware query using actual biomechanical signals.
    This directly impacts retrieval quality.
    """

    speed = data.get("speed", "unknown")
    length = data.get("length", "unknown")

    time_to_batsman = data.get("time_to_batsman", "unknown")
    total_movement = data.get("total_movement", "unknown")

    runup = data.get("runup_stability", "unknown")

    ffc_brace = data.get("ffc_brace", "unknown")
    ffc_head = data.get("ffc_head", "unknown")

    release_arm = data.get("release_arm", "unknown")
    release_lean = data.get("release_lean", "unknown")

    follow_through = data.get("follow_through", "unknown")

    # 🔥 Build signal-aware query
    query = f"""
    Cricket fast bowling biomechanics and injury risk analysis.

    Bowling speed: {speed} km/h
    Delivery length: {length}

    Ball travel time: {time_to_batsman}
    Ball movement: {total_movement}

    Run-up stability: {runup}

    Front foot contact:
    - knee brace: {ffc_brace}
    - head position: {ffc_head}

    Release mechanics:
    - arm slot: {release_arm}
    - body lean: {release_lean}

    Follow-through quality: {follow_through}

    Analyze:
    - joint loading patterns
    - injury risk (knee, back, shoulder, ankle)
    - biomechanical inefficiencies
    - stress during deceleration phase
    """

    return query.strip()