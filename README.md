# AI Cricket Analysis System

## Overview

This project is an AI-based cricket analysis system that processes cricket delivery data, generates structured cricket insights, and performs both segment-level and session-level analysis using LLM-based agents.

The system includes:

- Middleware pipeline for cricket data processing
- Multi-agent delivery analysis
- Session-level metrics and analysis
- Langfuse tracing support
- API and GCS integrations

---

# Project Flow

## Segment Analysis Flow

```
API Data + Artifacts
        ↓
Environment Setup
        ↓
Middleware Pipeline
        ↓
Structured Delivery JSON
        ↓
Multi-Agent Analysis
        ↓
Save Analysis to DB
```

## Session Analysis Flow

```
Batch Session API Data
        ↓
Session Metrics Builder
        ↓
Session LLM Agent
        ↓
Save Session Analysis
```

---

# Project Structure

```text
app/
│
├── core/
│   ├── config.py
│   ├── logging_setup.py
│   └── request_logging.py
│
├── pipeline/
│   │
│   ├── RAG/
│   │
│   ├── segment_pipeline/
│   │   ├── agents/
│   │   │   ├── batting_agent.py
│   │   │   ├── bowling_agent.py
│   │   │   ├── commentator_agent.py
│   │   │   ├── fielding_agent.py
│   │   │   └── physio_agent.py
│   │   │
│   │   ├── middleware/
│   │   │   ├── biomechanics_analyzer.py
│   │   │   ├── data_extractor.py
│   │   │   ├── data_loader.py
│   │   │   ├── data_merger.py
│   │   │   ├── data_validator.py
│   │   │   ├── feature_engine.py
│   │   │   ├── json_builder.py
│   │   │   ├── physics_engine.py
│   │   │   ├── pipeline.py
│   │   │   └── stats_engine.py
│   │   │
│   │   ├── runner.py
│   │   ├── prompt_manager.py
│   │   └── state.py
│   │
│   └── session_pipeline/
│       └── session/
│           ├── session_agent.py
│           ├── session_metrics.py
│           └── session_schema.py
│
├── schemas/
│   └── requests.py
│
├── services/
│   ├── api_client.py
│   └── gcs_client.py
│
├── utils/
│   └── langfuse_utils.py
│
├── main.py
├── requirements.txt
├── Dockerfile
└── README.md
```

---

# Segment Pipeline

The segment pipeline processes delivery-level cricket data.

## Middleware Responsibilities

The middleware layer handles:

- Data loading
- Data extraction
- Data validation
- Data merging
- Physics calculations
- Feature generation
- JSON construction
- Biomechanics analysis
- Statistics generation

---

# Multi-Agent Analysis

Each delivery is analyzed using multiple agents.

## Agents

### Commentator Agent
Generates delivery commentary.

### Batting Agent
Analyzes batting-related aspects of the delivery.

### Bowling Agent
Analyzes bowling-related insights.

### Fielding Agent
Analyzes fielding impact and context.

### Physio Agent
Processes biomechanics and physical movement related analysis.

---

# Session Pipeline

The session pipeline performs complete session-level analysis.

## Session Components

### Session Metrics
Builds aggregated session metrics from batch insight data.

### Session Agent
Generates overall session-level LLM analysis.

---

# Langfuse Tracing

The project uses Langfuse tracing for:

- Session tracking
- Delivery-level metadata
- Tags
- LLM tracing

Trace metadata includes:

- analysis_type
- total_deliveries
- biomechanics availability
- session_id
- delivery index

---

# External Integrations

## API Client

Used for:

- Fetching segment insight data
- Fetching batch session data
- Saving segment analysis
- Saving session analysis

## GCS Client

Used for downloading:

- final_combined.json
- bowler_keypoints.csv

---

# Technologies Used

- Python
- Pandas
- NumPy
- LangChain
- Google Gemini
- Langfuse
- Pydantic
- FAISS
- Sentence Transformers

---

# Analysis Types

## Segment Analysis
Processes and analyzes individual deliveries.

## Session Analysis
Processes complete cricket sessions using aggregated metrics.

---

# Main Entry Point

`main.py` handles:

- Request parsing
- Environment setup
- Segment analysis execution
- Session analysis execution
- DB save operations
- Cleanup
- Logging
- Langfuse flushing

---

# Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Running the Project

```bash
python main.py '<json_payload>'
```

---

# Notes

- Supports both local execution and cloud job execution
- Segment and session analysis are handled separately
- Temporary downloaded artifacts are cleaned after successful execution
- Built using modular pipelines and agent-based analysis architecture
