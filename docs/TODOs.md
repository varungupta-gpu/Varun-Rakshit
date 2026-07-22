# TODOs

## Goals for the week
1. Wire this job to run in cloud environment as a part of a ball segment analysis flow: Segment Upload -> CV processing -> LLM analysis. Technical details below.
2. Run this e2e across multiple segments (mix of good and bad CV detections) and show on Admin Panel for easy (manual) eval.
3. Split each area of commentary into a separate agent, with it's own RAG and Wiki.

## [Task 1] Run in Cloud and wire with actual data and flow
### Overview
This repo will run as a GCP cloud run job and will be triggered as a part of the per segment analysis. Cloud run jobs run as a python script, so no changes in the triggerring part.

### Inputs & Environment Setup
This takes in ids for our DB entities. The main ones are:
 - request_id: str
 - video_id: str  # Video ID used for GCS folder structure
 - insight_id: str  # Insight ID to get trajectory JSON data
 - segment_id: Optional[str] = None #segment id used to getting the gs file path
 - segment_insight_id: Optional[str] = None #segment insight id used to getting the trajectory json data and update the trajectory data 
 - api_base_url: str  # API base URL (used to save data back to DB)
 - bearer_access_token: str # Bearer access token for authentication to all APIs

It needs to call this API `{api_base_url.rstrip('/')}/api/v1/insights/{insight_id}/segments/{segment_insight_id}`. You can see usage of this api in this repo - `https://github.com/sportzengage/video-processing-pipelines`. This will return data in the same format as you have in `delivery_segments_valid.json` and will also contain the `dqi_report` in the data. This will also have gcs links to the artifacts - look for the `artifacts->final_csv` to get the gcs path - download it locally.

### Output format
Instead of plain text, we should have it wrapped inside a json with different sections being named json keys.

### Saving output
Once the processing is complete the results needs to be saved back to the DB by calling another API - `{self.base_url}/api/v1/insights/{insight_id}/update` - refer to `https://github.com/sportzengage/video-processing-pipelines` for usage example.


## [Task 2] Update the framework for agentic architecture
### Overview
Our current framework only has one agent that takes data input and provides llm analysis on top of it. We need to update the framework to act as an agentic system with multiple agents, each agent will analysis a particular delivery for a particular analysis.

### Agents Types
#### 1. Commentator Agent
  #### a. For Batter:
    On the basis of given data, analyse and provide a commentary (batting) for the played shot.
  #### b. For Bowler:
    On the basis of given data, analyse and provide a commentary (bowling) for the bowled delivery.
#### 2. Batting Agent
  #### a. For Batter:
    On the basis of given data, analyse potential shots the batter could have played on the given delivery.
  #### b. For Bowler:
    On the basis of given data, analyse potential shots a batter (rhs/lhs) can opt to play on the given delivery.
#### 3. Fielding Agent
  #### a. For Batter:
    On the basis of given data, analyse fielding positions the bowler could set for the batter.
  #### b. For Bowler:
    On the basis of given data, analyse potential fielding positions the bowler can set (powerplay, middle overs, death overs), based on bowled delivery.
#### 4. Bowling Agent
  #### a. For Batter:
    On the basis of given data, analyse the variations a bowler can try using the same line and length for the batter (left/right handed).
  #### b. For Bowler:
    On the basis of given data, analyse the variations a bowler can try using the same line and length (for both lhs/rhs batter).
#### 5. Physio Agent
  #### a. For Batter:
    On the basis of given data, analyse the biomechanics of the batter.
  #### b. For Bowler:
    On the basis of given data, analyse the biomechanics of the bowler.

### Requirements
1. Prepare json data for inference
2. Use langgraph to orchestrate the agents
3. Each agent will have its own RAG and Wiki
4. Each agent will have it's own prompt and model(may be)*
5. Each agent will have a separate system prompt for providing it with an identity/nature
6. Keep all analysis output in json