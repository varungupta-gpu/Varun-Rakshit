from app.pipeline.segment_pipeline.state import create_initial_state
from app.pipeline.segment_pipeline.agents.commentator_agent import run_commentator_agent


def test_commentator():
    # ---------- SAMPLE DELIVERY ----------
    sample_delivery = {
        "metadata": {
            "speed_kmph": 142
        },
        "features": {
            "line": "off stump",
            "length": "good length",
            "swing_type": "outswing"
        }
    }

    # ---------- CREATE STATE ----------
    state = create_initial_state(sample_delivery)

    # ---------- RUN AGENT ----------
    state = run_commentator_agent(state)

    # ---------- OUTPUT ----------
    print("\n=== COMMENTATOR OUTPUT ===\n")
    print(state["outputs"]["commentator"])


if __name__ == "__main__":
    test_commentator()