# Commands

## Run job from command line
```bash
python main.py '{"request_id":"test-1","video_id":"123","segment_id":"012","insight_id":"789","segment_insight_id":"sdfs","api_base_url":"http://localhost:8000","bearer_access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5OTk5OTk5OTkyIiwiZXhwIjoxNzkxNDQ4MTc3fQ.4UqxeVtlrtZDy20IFJipdkpgD4_eSSsNynroW__NL0g"}'
```


## Run job on cloud run
```bash
gcloud run jobs execute analysis-processor \
    --region=asia-south1 \
    --project=video-backend-dev \
    --args='{"request_id":"test-cloud-shamik-20260416-test","video_id":"e9a86edc-b22e-4421-9a12-d07dd492e5a7","segment_id":"e4e51ee8-2e5a-43e9-9c33-92f85e8387b6","insight_id":"207ae441-c327-4199-b53e-ae2c63c70595","segment_insight_id":"9a728461-c82e-4016-b23b-8598a5421041","api_base_url":"https://video-insights-api-988584008199.asia-south1.run.app","bearer_access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5OTk5OTk5OTkyIiwiZXhwIjoxNzkxNDQ4MTc3fQ.4UqxeVtlrtZDy20IFJipdkpgD4_eSSsNynroW__NL0g"}'
```


```
bash
./build_deploy_v2.sh --deploy --job analysis-processor
```