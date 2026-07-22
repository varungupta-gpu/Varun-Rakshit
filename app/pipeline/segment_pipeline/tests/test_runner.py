import json
from app.pipeline.segment_pipeline.runner import run_full_analysis


def test_runner():
    output = run_full_analysis()

    print("\n=== FINAL OUTPUT ===\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    test_runner()