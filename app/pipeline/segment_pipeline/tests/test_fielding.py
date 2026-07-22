import json
from app.pipeline.segment_pipeline.state import create_initial_state
from app.pipeline.segment_pipeline.agents.fielding_agent import run_fielding_agent


def test_fielding():
    sample_delivery = {
        "metadata": {
            "speed_kmph": 145
        },
        "features": {
            "line": "off stump",
            "length": "full",
            "swing_type": "outswing"
        }
    }

    state = create_initial_state(sample_delivery)

    state = run_fielding_agent(state)

    print("\n=== FIELDING OUTPUT ===\n")
    print(json.dumps(state["outputs"]["fielding"], indent=2))


if __name__ == "__main__":
    test_fielding()