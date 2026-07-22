import json
from app.pipeline.segment_pipeline.state import create_initial_state
from app.pipeline.segment_pipeline.agents.bowling_agent import run_bowling_agent


def test_bowling():
    sample_delivery = {
        "metadata": {
            "speed_kmph": 140
        },
        "features": {
            "line": "off stump",
            "length": "good length",
            "swing_type": "outswing"
        }
    }

    state = create_initial_state(sample_delivery)

    state = run_bowling_agent(state)

    print("\n=== BOWLING OUTPUT ===\n")
    print(json.dumps(state["outputs"]["bowling"], indent=2))


if __name__ == "__main__":
    test_bowling()