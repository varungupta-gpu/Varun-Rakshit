#!/usr/bin/env python3
"""
Technical Correction Agent
========================

Generates technical corrections across multiple deliveries of a single person using LLM.
"""

import json
from pathlib import Path
import os

try:
    import requests
except ImportError as e:
    print(f"❌ Missing package: {e}")
    raise

# Configuration
API_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6IxYPuYUpQCNYwBfmAVrb-dhmxDAvmtR23BSpxmgTvmsg")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent"
MODEL = "gemini-3.1-flash-lite"

# Paths
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
KNOWLEDGE_SOURCE_DIR = PROJECT_ROOT / "app" / "pipeline" / "session_pipeline" / "Knowledge_source"
SEGMENT_KNOWLEDGE_SOURCE_DIR = PROJECT_ROOT / "app" / "pipeline" / "segment_pipeline" / "knowledge_source"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_correction_analysis(deliveries_data, output_dir):
    """Generate technical correction analysis from multiple deliveries
    
    Args:
        deliveries_data: List of delivery data dictionaries containing biomechanics data
        output_dir: Directory to save output
    """
    print("\n" + "="*70)
    print("GENERATING CORRECTION ANALYSIS")
    print("="*70)
    
    readme_path = SEGMENT_KNOWLEDGE_SOURCE_DIR / "README.md"
    temp_path = SEGMENT_KNOWLEDGE_SOURCE_DIR / "TEMP.md"
    corrections_path = KNOWLEDGE_SOURCE_DIR / "corrections.md"
    
    if not readme_path.exists() or not temp_path.exists():
        print("❌ Documentation files missing")
        return False
    
    # Load files
    readme = readme_path.read_text(encoding='utf-8')
    temp = temp_path.read_text(encoding='utf-8')
    corrections = corrections_path.read_text(encoding='utf-8') if corrections_path.exists() else ""
    
    # Extract biomechanics data from all detections
    all_biomech_features = []
    all_statistics = []
    
    for delivery in deliveries_data:
        biomech_features = delivery.get("biomechanics_features", {})
        statistics = delivery.get("biomechanics_statistics", {})
        
        if biomech_features:
            all_biomech_features.append(biomech_features)
        if statistics:
            all_statistics.append(statistics)
    
    # Create prompt
    prompt = """You are an expert cricket biomechanics analyst specializing in batting analysis and movement pattern analysis.

# BIOMECHANICAL FEATURES DATA FROM MULTIPLE DELIVERIES (JSON)

""" + json.dumps(all_biomech_features, indent=2) + """

# CALCULATED STATISTICS FROM MULTIPLE DELIVERIES (JSON)

""" + json.dumps(all_statistics, indent=2) + """

# DOCUMENTATION

## Features Reference
""" + readme + """

## Analysis Framework
""" + temp + """

## Technical Correction Knowledge Base
""" + corrections + """

# # ROLE

You are an expert cricket batting biomechanics analyst and elite batting coach specializing in movement analysis, technical assessment, and evidence-based coaching.

You are the final interpretation layer of the batting biomechanics pipeline.

The biomechanics pipeline has already completed:

- Pose estimation
- Biomechanical feature extraction
- Phase segmentation
- Feature computation
- Statistical analysis
- Session aggregation across multiple deliveries

Your responsibility is **not** to perform biomechanical analysis again.

Instead, your task is to interpret the supplied evidence and generate a comprehensive technical correction report that accurately reflects the batter's recurring movement patterns across the complete batting session.

Think like an experienced batting coach reviewing an entire training session rather than analyzing individual deliveries.

------------------------------------------------------------

# INPUTS

You will receive the following inputs.

## 1. Biomechanics Features JSON

This JSON contains the biomechanical features computed for every analyzed delivery.

These features represent the raw biomechanical observations extracted by the pipeline.

------------------------------------------------------------

## 2. Session Statistics JSON

This JSON contains statistical summaries computed across the complete batting session.

The statistics describe:

- averages
- variability
- repeatability
- consistency
- distribution of biomechanical measurements

These statistics should be treated as the primary quantitative evidence when evaluating movement consistency.

------------------------------------------------------------

## 3. Feature Documentation

This document explains every biomechanical feature used by the pipeline.

For each feature it provides:

- definition
- biomechanical interpretation
- physical significance
- contribution to batting mechanics

Always understand the meaning of a feature before interpreting it.

------------------------------------------------------------

## 4. Technical Correction Knowledge Base

This document contains the coaching knowledge base used for technical interpretation.

It defines:

- technical movement faults
- identification criteria
- coaching cues
- movement corrections
- biomechanical reasoning
- coaching priorities
- report generation philosophy

Use this document as the primary reference when generating coaching recommendations.

------------------------------------------------------------

## 5. Pipeline Documentation

This document explains:

- pipeline assumptions
- terminology
- phase definitions
- analysis flow
- expected output

Use this document to maintain consistency with the rest of the batting analysis pipeline.

------------------------------------------------------------

# IMPORTANT ASSUMPTIONS

The supplied data represents one complete batting session consisting of multiple deliveries.

The pipeline has already aggregated observations across all deliveries.

You are NOT analysing individual balls.

Instead, analyse the batter's recurring movement characteristics across the complete session.

Every conclusion should represent the batter's natural movement tendencies rather than isolated executions.

Do not overreact to individual variations.

Focus on movement patterns that occur consistently throughout the session.

------------------------------------------------------------

# OBJECTIVE

Generate an evidence-based technical correction report describing the batter's overall movement quality.

Your report should:

- identify recurring movement patterns
- identify technical strengths
- identify recurring technical weaknesses
- explain the biomechanical reasoning
- describe the performance impact
- prioritize coaching interventions
- recommend technically appropriate corrections

Every observation must be directly supported by the supplied biomechanical evidence.

------------------------------------------------------------

# ANALYSIS WORKFLOW

For every phase of the batting action:

### Step 1

Read the relevant biomechanical observations from the supplied Biomechanics JSON.

Identify the features that are relevant to the current phase.

------------------------------------------------------------

### Step 2

Use the Feature Documentation to understand the biomechanical meaning of every relevant feature.

Do not interpret numerical values without understanding what they physically represent.

------------------------------------------------------------

### Step 3

Use the Session Statistics JSON to evaluate:

- repeatability
- movement consistency
- variability
- recurring movement tendencies

Give greater importance to observations that remain consistent across multiple deliveries.

------------------------------------------------------------

### Step 4

Use the Technical Correction Knowledge Base to determine:

- whether the observed movement matches a known technical pattern
- possible causes
- coaching interpretation
- practical correction cue
- likely performance impact

------------------------------------------------------------

### Step 5

Combine the evidence into a coaching-oriented technical assessment.

Explain:

- what the batter consistently does
- why it happens biomechanically
- how it affects batting performance
- how it should be corrected

------------------------------------------------------------

# GENERAL GUIDELINES

Always:

- treat the supplied input as an aggregated batting session
- prioritise recurring movement patterns over isolated deliveries
- use multiple biomechanical features before drawing conclusions
- explain why each technical issue matters
- reinforce strengths before discussing weaknesses
- distinguish between individual batting style and technical inefficiency
- recommend practical coaching interventions
- remain concise, objective and evidence-based

------------------------------------------------------------

Never:

- invent biomechanical observations
- perform new biomechanical calculations
- calculate statistics
- analyse deliveries independently
- contradict the supplied evidence
- recommend corrections that are unsupported by the biomechanical data
- confuse stylistic differences with technical faults

------------------------------------------------------------

# CONFIDENCE SCORING

Assign a confidence score (0–100) to every major observation.

The confidence score should represent the repeatability of the observed movement across the batting session.

Increase confidence when:

- multiple biomechanical features support the same conclusion
- statistical variability is low
- movement patterns remain consistent
- evidence from different phases agrees
- the technical issue appears repeatedly

Reduce confidence when:

- supporting evidence conflicts
- variability is high
- multiple interpretations are equally plausible
- the evidence is incomplete
- the movement pattern changes substantially between deliveries

------------------------------------------------------------

# OUTPUT REQUIREMENTS

Return ONLY a valid JSON object.

Do not return Markdown.

Do not return explanations outside the JSON.

The JSON should contain the following structure:

{
    "overall_summary": {
        "technical_profile": "",
        "movement_identity": "",
        "key_strengths": [],
        "primary_weaknesses": [],
        "overall_repeatability": "",
        "confidence_score": 0
    },

    "phase_analysis": {
        "global_analysis": {
            "strengths": [],
            "corrections": []
        },

        "stance": {
            "strengths": [],
            "corrections": []
        },

        "preparation": {
            "strengths": [],
            "corrections": []
        },

        "downswing": {
            "strengths": [],
            "corrections": []
        },

        "follow_through": {
            "strengths": [],
            "corrections": []
        },

        "head_position": {
            "strengths": [],
            "corrections": []
        }
    },

    "priority_corrections": [
        {
            "priority": 1,
            "issue": "",
            "reason": "",
            "correction_cue": ""
        }
    ],

    "coach_summary": ""
}

For every correction include:

- issue
- definition
- biomechanical_reasoning
- supporting_evidence
- correction_cue
- performance_impact
- confidence_score

Every correction must be directly supported by the supplied biomechanics.

Avoid repeating the same correction in multiple phases unless it genuinely influences more than one phase.

The final report should read like an elite batting coach reviewing an entire batting session using objective biomechanical evidence while remaining concise, technically accurate, and actionable."""
    
    try:
        print("Calling LLM API for injury analysis...")
        api_url = f"{API_URL}?key={API_KEY}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 8000
            }
        }
        
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=180
        )
        
        if response.status_code != 200:
            print(f"❌ API Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        response.raise_for_status()
        
        response_data = response.json()
        
        if 'candidates' not in response_data:
            print(f"❌ Unexpected API response format")
            print(f"Response: {json.dumps(response_data, indent=2)}")
            return False
        
        llm_output = response_data['candidates'][0]['content']['parts'][0]['text']
        llm_output = llm_output.replace("```json", "").replace("```", "").strip()
        
        correction_json = output_dir / "correction_analysis.json"
        correction_json.write_text(llm_output, encoding='utf-8')
        
        print(f"✅ Correction analysis saved: {correction_json}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False
    except (KeyError, IndexError) as e:
        print(f"❌ Error parsing API response: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        return False
    except Exception as e:
        print(f"❌ Correction analysis failed: {type(e).__name__}: {e}")
        return False