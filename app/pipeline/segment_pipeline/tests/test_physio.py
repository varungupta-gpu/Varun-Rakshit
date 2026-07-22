import json
from app.pipeline.segment_pipeline.agents.biomechanics_agent import run_physio_agent

def test_physio():
    with open("data_processed/result.json", "r") as f:
        data = json.load(f)

    delivery = data["deliveries"][0]

# Inject biomechanics into delivery
    delivery["biomechanics"] = data.get("biomechanics", {})

    state = {
        "delivery": delivery,
        "outputs": {}
    }

    result_state = run_physio_agent(state)

    print("\n✅ PHYSIO OUTPUT:\n")
    print(json.dumps(result_state["outputs"]["physio"], indent=2))


if __name__ == "__main__":
    test_physio()