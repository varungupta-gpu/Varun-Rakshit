#!/usr/bin/env python3
"""
Combined Analysis Agent
========================

Analyzes stance and preparation similarities across multiple deliveries for the same batsman.
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


def generate_combined_analysis(deliveries_data, output_dir):
    """Generate combined analysis from multiple deliveries
    
    Args:
        deliveries_data: List of delivery data dictionaries containing biomechanics data
        output_dir: Directory to save output
    """
    print("\n" + "="*70)
    print("GENERATING COMBINED ANALYSIS")
    print("="*70)
    
    readme_path = SEGMENT_KNOWLEDGE_SOURCE_DIR / "README.md"
    temp_path = SEGMENT_KNOWLEDGE_SOURCE_DIR / "TEMP.md"
    style_path = KNOWLEDGE_SOURCE_DIR / "style.md"
    
    if not readme_path.exists() or not temp_path.exists():
        print("❌ Documentation files missing")
        return False
    
    # Load files
    readme = readme_path.read_text(encoding='utf-8')
    temp = temp_path.read_text(encoding='utf-8')
    style = style_path.read_text(encoding='utf-8') if style_path.exists() else ""
    
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
    prompt = f"""You are an expert cricket biomechanics analyst specializing in batting stance and preparation analysis across multiple deliveries.

# BIOMECHANICAL FEATURES DATA FROM MULTIPLE DELIVERIES (JSON)

{json.dumps(all_biomech_features, indent=2)}

# CALCULATED STATISTICS FROM MULTIPLE DELIVERIES (JSON)

{json.dumps(all_statistics, indent=2)}

# DOCUMENTATION

## Features Reference
{readme}

## Analysis Framework
{temp}

## Batter Base Analysis Documentation
{style}

# TASK

ROLE

You are an expert cricket batting biomechanics analyst and batting coach specializing in batting setup, movement organization, and technical base analysis.

Your task is to analyze the batter's natural batting base by evaluating the Stance and the first half of the Preparation phase across multiple deliveries.

Do not analyze individual shots independently. Instead, identify the recurring movement characteristics that define the batter's default setup, trigger movement, body organization, and movement consistency.

Always base your conclusions on the provided biomechanical evidence and avoid making unsupported assumptions. Every observation should be supported by multiple biomechanical features and should represent a recurring movement pattern rather than an isolated occurrence.

INPUTS

You will receive the following inputs.

1. Biomechanics Report

A JSON containing the computed biomechanical features extracted from multiple batting deliveries.

The report contains the raw biomechanical measurements for the Stance and Preparation phases.

2. Feature Statistics Report

A JSON containing statistical summaries of the biomechanical features across all analyzed deliveries.

These statistics describe the overall behaviour and repeatability of each biomechanical feature and should be treated as the primary quantitative evidence during analysis.

3. Batter Base Analysis Documentation

A reference document describing:

Scope of analysis
Analysis strategy
Areas to evaluate
Coaching objectives
Expected report structure

This document defines how the batter's natural batting base should be analyzed.

4. Batting Biomechanical Style Documentation

A reference document describing:

Stance styles
Preparation styles
Features associated with each style
Decision strategy
Style definitions

Use this document whenever stance or preparation styles need to be interpreted.

5. Biomechanical Feature Documentation

A reference document describing every biomechanical feature used by the pipeline.

This document explains:

Feature definition
Method of computation
Physical interpretation
Biomechanical significance

Always use this document to correctly interpret the provided biomechanical measurements.

OBJECTIVE

Analyze the batter's natural batting base across multiple deliveries.

The objective is not to analyze stroke execution or shot outcome.

Instead, determine the batter's default setup, initial movement strategy, and movement repeatability before the downswing begins.

The analysis should identify:

Overall Batting Base
Stance Style
Trigger Movement
Initial Weight Transfer
Body Organization
Head Position
Repeatability
Overall Technical Base Summary

The final report should describe the batter's natural movement identity before stroke execution.

ANALYSIS PROCESS

For every analysis category:

Step 1 — Extract Evidence

Read the relevant biomechanical measurements and statistical summaries from the provided JSON reports.

Collect both primary and supporting biomechanical features associated with the category being analyzed.

Since multiple deliveries are provided, evaluate the overall behaviour across the complete dataset rather than individual deliveries.

Step 2 — Interpret Features

Interpret every extracted feature using the Biomechanical Feature Documentation.

Understand the physical meaning of every measurement before drawing conclusions.

Do not compare numerical values without understanding their biomechanical significance.

Step 3 — Identify Recurring Patterns

Instead of evaluating individual deliveries independently, identify movement patterns that occur consistently across the majority of deliveries.

Focus on:

Repeatability
Consistency
Stability
Common movement tendencies
Natural batting habits

Ignore isolated variations unless they occur frequently.

Step 4 — Compare Candidate Styles

Where applicable, compare the observed movement behaviour against the candidate styles described in the Batting Biomechanical Style Documentation.

Evaluate the complete movement pattern rather than isolated feature values.

For stance and preparation, consider both primary and supporting biomechanical features before selecting the dominant style.

Step 5 — Generate Analysis

Generate a detailed coaching-oriented assessment describing the batter's natural batting base.

The explanation should clearly describe:

What the batter naturally does.
Which biomechanical evidence supports the observation.
How consistent the movement pattern is across deliveries.
How the observed movement contributes to the batter's technical setup.
ANALYSIS GUIDELINES

While performing the analysis:

Evaluate the batter across all provided deliveries rather than individual shots.
Prioritize recurring movement patterns over isolated observations.
Use multiple biomechanical features before drawing conclusions.
Consider both primary and supporting biomechanical evidence.
Focus only on the Stance and early Preparation phases.
Do not discuss downswing, follow-through, shot execution, bat path, or shot outcome.
Every observation should be directly supported by the provided biomechanical evidence.

If conflicting evidence exists:

Determine which movement pattern appears most consistently.
Explain the biomechanical reasoning.
Reduce the confidence score appropriately.

Never invent movement characteristics that are not supported by the provided inputs.

CONFIDENCE SCORE

Every major observation should include a confidence score between 0 and 100.

The confidence score represents how consistently the observed movement pattern appears across the analyzed deliveries.

Increase confidence when:

Multiple deliveries demonstrate the same movement pattern.
Multiple biomechanical features independently support the same conclusion.
Statistical measurements remain consistent across deliveries.
Movement variability is low.
The observed movement closely matches the characteristics described in the reference documentation.
The batter demonstrates a repeatable technical setup.

Reduce confidence when:

Deliveries exhibit inconsistent movement patterns.
Supporting biomechanical features disagree.
Statistical variability is high.
Multiple interpretations appear equally plausible.
The movement pattern changes significantly between deliveries.
The available biomechanical evidence is weak or incomplete.

Confidence should represent the repeatability and consistency of the batter's movement rather than the certainty of the language model.

OUTPUT REQUIREMENTS

Return the analysis using the report structure defined in the Batter Base Analysis Documentation.

The report should include:

Overall Base Summary
Stance Analysis
Trigger Movement Analysis
Initial Weight Transfer
Body Organization
Head Position
Repeatability Assessment
Overall Technical Base Summary

Every major observation should include:

Observation
Biomechanical Reasoning
Supporting Evidence
Confidence Score

Do not invent additional sections.

Do not include shot-specific analysis.

Do not discuss the downswing or follow-through.

Do not generate commentary outside the requested report structure.

FINAL SUMMARY

The final summary should combine observations from all analyzed deliveries into a concise assessment of the batter's natural batting base.

The summary should describe:

Default batting setup
Initial movement strategy
Trigger characteristics
Lower-body organization
Upper-body organization
Balance and posture
Movement repeatability
Overall technical foundation

The summary should read like a report written by an experienced batting biomechanics consultant after observing the batter over multiple deliveries during the setup and initial loading phases.

The emphasis should be on identifying the batter's natural technical base, highlighting recurring movement habits rather than describing individual deliveries or specific shots.

Return a JSON with the following structure:
{{
    "stance_analysis": {{
        "consistency_score": 0-100,
        "dominant_stance_style": "style_name",
        "stance_variations": ["list of observed variations"],
        "analysis": "detailed analysis"
    }},
    "preparation_analysis": {{
        "consistency_score": 0-100,
        "dominant_prep_style": "style_name",
        "prep_variations": ["list of observed variations"],
        "analysis": "detailed analysis"
    }},
    "overall_summary": "summary of combined analysis"
}}

Do not return markdown, explanations, or commentary outside the JSON."""
    
    try:
        print("Calling LLM API for combined analysis...")
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
        
        combined_json = output_dir / "combined_analysis.json"
        combined_json.write_text(llm_output, encoding='utf-8')
        
        print(f"✅ Combined analysis saved: {combined_json}")
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
        print(f"❌ Combined analysis failed: {type(e).__name__}: {e}")
        return False