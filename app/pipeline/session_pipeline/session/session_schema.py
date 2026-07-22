

EMPTY_SESSION_SCHEMA = {

    # =====================================================
    # SESSION METADATA
    # =====================================================

    # "session_metadata": {

    #     "session_id": "",

    #     "video_id": "",

    #     "total_segments": 0
    # },

    # =====================================================
    # SPEED ANALYSIS
    # =====================================================

    "speed_analysis": {

        "average_speed_kmph": 0,

        "maximum_speed_kmph": 0,

        "minimum_speed_kmph": 0,

        "median_speed_kmph": 0,

        "speed_std_deviation": 0,

        "speed_variance": 0,

        "fastest_delivery": {

            "speed_kmph": 0
        },

        "slowest_delivery": {

            "speed_kmph": 0
        }
    },

    # =====================================================
    # RELEASE ANALYSIS
    # =====================================================

    "release_analysis": {

        "average_release_height_m": 0,

        "max_release_height_m": 0,

        "min_release_height_m": 0,

        "release_height_std_deviation": 0
    },

    # =====================================================
    # BOUNCE ANALYSIS
    # =====================================================

    "bounce_analysis": {

        "average_bounce_x": 0,

        "average_bounce_y": 0
    },

    # =====================================================
    # TRAJECTORY ANALYSIS
    # =====================================================

    "trajectory_analysis": {

        "average_trajectory_points": 0,

        "average_flight_time_s": 0,

        "average_distance_3d_m": 0,

        "average_speed_mps": 0
    },

    # =====================================================
    # STABILITY ANALYSIS
    # =====================================================

    "stability_analysis": {

        "average_rmse": 0,

        "average_smoothness": 0,

        "average_bad_jumps": 0
    },

    # =====================================================
    # SESSION BIOMECHANICS ANALYSIS
    # =====================================================

    "session_biomechanics_analysis": {
        "segment_ids": [],
        "segment_insight_ids": [],
        "segment_llm_insights": [],
        "segment_biomechanics_reports": []
    }
}