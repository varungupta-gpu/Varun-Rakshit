import json
import subprocess

# --------------------------------------------------
# Common payload (same for every request)
# --------------------------------------------------
BASE_PAYLOAD = {
    "request_id": "abx",
    "user_id": "12345678",
    "video_id": "fa7c87e5-08b5-4aea-bf5d-a685b470104b",
    "llm_insight_id": "7de40a7b-672b-4176-bea3-185f7d358293",
    "analysis_type": "segment",
    "player_id": "4e21ce82-bb15-4caf-b825-c9a859579679",
    "api_base_url": "https://video-insights-api-dev-wmoq36zjfq-el.a.run.app",
    "bearer_access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5OTk5OTk5OTk1Iiwicm9sZSI6InVzZXIiLCJleHAiOjE3ODQ3MDM1ODV9.W971vKpV_1BxGez9DGkVoyGL5NQmbjCti9gBM9KH1yc"
}

# --------------------------------------------------
# Segment ID, Segment Insight ID
# --------------------------------------------------
SEGMENTS = [
    ("8b0a450f-04ac-4bd3-a9e6-58156c1f1d75", "037f5052-e296-4b68-bae5-c0798e5da104"),
    ("875188bd-647e-4ef4-83ad-2f535ebcaa4d", "f476c49f-9b9a-4c2c-b7f6-2cf4a168d66d"),
    ("3eb2b36c-9fe0-4ff7-92b9-639212e00c76", "93c491aa-b5dc-41ef-99fe-7f2cc97f4fcd"),
    ("bca4ffb0-e41a-4296-8529-b57c1aa6da1f", "34069184-9677-4760-ad32-c67c9563c39c"),
    ("f1a15a53-8897-494b-9560-f8bd5aff3154", "fa152667-f13b-445c-8574-a3ae89510dfa"),
    ("8086ddf9-7329-4746-bf8d-7ec958ce1ca6", "c73e9e4a-6d2e-455a-8d45-b84679bb89fc"),
    ("756c734d-d0d1-4552-9c2e-2d5e1ea5c1b8", "de25a21d-53f3-405e-bb89-91af4f20591b"),
    ("f74c47ed-e3a8-4837-a8f0-91797403c240", "e0ac607a-1542-444c-98fd-d3f0d17d5531"),
    ("ab007ad6-763e-4971-a20e-4b670742b969", "270e6099-1507-4d47-a4cc-db68c0b26817"),
    ("56da660d-21fe-4c1b-926d-1e8dba22b494", "55598a25-6a8c-4ddb-be7b-d88583051161"),
    ("c52b9ab3-c454-49d3-8b74-7f3a957022c0", "9eb4c0e2-9af3-4e37-b382-9f87995d3f36"),
    ("af05c466-51a5-45f6-9463-6115be87fec9", "7999fd92-5f64-4fd7-8c79-e915c4e49c2c"),
    ("c28dc68e-fcba-440e-9e27-116547b5a057", "91e1ec87-d90c-44f3-a234-9f0aabf19f0e"),
    ("778ea8fb-af1e-4d4d-90c2-4100f26ea3f4", "6bc37e33-e31d-4035-8d9a-ed9d7df53f79"),
    ("be307b8a-9526-4a20-a3cc-cb95bae24713", "56deb9b2-2769-4c97-a17c-0e5da9e6a28a"),
    ("4ca544c0-252e-43a8-bf47-46e52b0f88c4", "0dd40eed-3f6f-4a0e-b308-17def8e14607"),
    ("985240e5-5096-4703-901d-80ab090a6ceb", "ac341f19-094c-4218-9220-9d651dee1de3"),
    ("a8009ff2-d327-4355-a53f-b551637d829f", "327fbc72-bde6-4cce-b4a8-0229a6488201"),
    ("1777d9a0-140a-4ed0-b393-0e324b28032d", "3dd4f497-89b0-43c7-9fe4-6e53b7a09ec1"),
    ("8941c284-63b4-4541-8215-446e7ec3cb0e", "e2fb152c-53c2-4154-8be4-eac996f8aa4a"),
]

# --------------------------------------------------
# Run
# --------------------------------------------------
total = len(SEGMENTS)

for idx, (segment_id, segment_insight_id) in enumerate(SEGMENTS, start=1):
    payload = BASE_PAYLOAD.copy()
    payload["segment_id"] = segment_id
    payload["segment_insight_id"] = segment_insight_id

    print(f"\n[{idx}/{total}] Running")
    print(f"Segment ID         : {segment_id}")
    print(f"Segment Insight ID : {segment_insight_id}")

    subprocess.run(
        ["python", "main.py", json.dumps(payload)],
        check=True
    )

print("\n✅ All segments completed successfully.")