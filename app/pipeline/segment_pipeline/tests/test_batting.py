import json

from app.pipeline.segment_pipeline.state import create_initial_state
from app.pipeline.segment_pipeline.agents.batting_agent import run_batting_agent

def test_batting():
    sample_delivery = {
        "metadata": {
            "speed_kmph": 138
        },
        "features": {
            "line": "middle stump",
            "length": "short length",
            "swing_type": "none"
        }
    }

    state = create_initial_state(sample_delivery)

    state = run_batting_agent(state)

        # ✅ CLEAN FINAL OUTPUT
    print("\n=== BATTING OUTPUT ===\n")
    print(json.dumps(state["outputs"]["batting"], indent=2))

if __name__ == "__main__":
    test_batting()