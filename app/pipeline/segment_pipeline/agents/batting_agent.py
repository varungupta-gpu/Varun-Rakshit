#!/usr/bin/env python3
"""
Batting LLM Analysis Agent
===========================

Generates LLM analysis from biomechanics data and statistics.
"""

import json
from pathlib import Path

try:
    import pandas as pd
    import requests
except ImportError as e:
    print(f"❌ Missing package: {e}")
    raise

# Configuration
import os
API_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6IxYPuYUpQCNYwBfmAVrb-dhmxDAvmtR23BSpxmgTvmsg")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent"
MODEL = "gemini-3.1-flash-lite"

# Paths
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
KNOWLEDGE_SOURCE_DIR = Path(__file__).resolve().parents[1] / "knowledge_source"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_llm_analysis(biomech_features_dict, statistics_dict, output_dir):
    """Generate LLM analysis from in-memory data
    
    Args:
        biomech_features_dict: Dictionary of biomechanics features from pipeline
        statistics_dict: Dictionary of statistics from pipeline
        output_dir: Directory to save output
    """
    print("\n" + "="*70)
    print("GENERATING LLM ANALYSIS")
    print("="*70)
    
    readme_path = KNOWLEDGE_SOURCE_DIR / "README.md"
    temp_path = KNOWLEDGE_SOURCE_DIR / "TEMP.md"
    
    if not readme_path.exists() or not temp_path.exists():
        print("❌ Documentation files missing")
        return False
    
    # Load files
    readme = readme_path.read_text(encoding='utf-8')
    temp = temp_path.read_text(encoding='utf-8')
    
    # Use in-memory data directly
    stats_data = statistics_dict
    biomech_json = biomech_features_dict if isinstance(biomech_features_dict, list) else [biomech_features_dict]
    
    # Create prompt
    prompt = f"""You are an expert cricket biomechanics analyst.

        # BIOMECHANICAL FEATURES DATA (JSON)

        {json.dumps(biomech_json, indent=2)}

        # CALCULATED STATISTICS (JSON)

        {json.dumps(stats_data, indent=2)}

        # DOCUMENTATION

        ## Features Reference
        {readme}

        ## Analysis Framework
        {temp}

        # TASK

        ROLE

        You are an expert cricket batting biomechanics analyst and batting coach specializing in technical movement analysis.

        Your task is to analyze the provided batting biomechanics and identify the movement characteristics that best describe the batter's technique.

        Do not classify batting styles using isolated feature values or predefined thresholds. Instead, evaluate the complete biomechanical evidence and determine the dominant movement patterns observed throughout the batting action.

        Always base your conclusions on the provided evidence and avoid making unsupported assumptions. Every selected movement style should be supported by multiple biomechanical observations rather than a single feature.

        INPUTS

        You will receive the following inputs.

        1. Biomechanics Report

        A JSON containing the computed biomechanical features extracted from the batting sequence.

        This report contains the raw biomechanical measurements computed for every batting phase.

        2. Feature Statistics Report

        A JSON containing statistical summaries of the biomechanical features across the batting phases.

        These statistics describe the overall behaviour of each biomechanical feature throughout the corresponding phase and should be treated as the primary quantitative evidence during analysis.

        3. Biomechanical Feature Documentation

        A reference document describing every biomechanical feature used by the pipeline.

        This document explains:

        Feature definition
        Physical interpretation
        Method of computation
        Biomechanical significance

        Use this document whenever a feature needs to be interpreted.

        4. Biomechanical Style Analysis Documentation

        A reference document describing:

        Batting phases
        Candidate movement styles
        Features associated with each style
        Decision strategy
        Style definitions
        Expected output format

        This document should be treated as the authoritative guide for batting style classification.

        OBJECTIVE

        Analyze the batter's biomechanics and determine the movement styles that best represent the observed batting action.

        The analysis should identify:

        Overall Shot Type
        Stance Style
        Preparation Style
        Downswing Style
        Follow-Through Style
        Head Position
        Overall Movement Summary

        The objective is to describe the batter's complete movement profile rather than simply reporting feature values.

        ANALYSIS PROCESS

        For every movement category:

        Step 1 — Extract Evidence

        Read the relevant biomechanical measurements and statistical summaries from the provided JSON reports.

        Identify the primary and supporting biomechanical features associated with the movement category.

        Step 2 — Interpret Features

        Interpret the extracted measurements using the Biomechanical Feature Documentation.

        Understand what each feature represents biomechanically before attempting any classification.

        Do not compare raw numbers without understanding their physical meaning.

        Step 3 — Compare Candidate Styles

        Compare the observed movement behaviour against every candidate style defined in the Biomechanical Style Analysis Documentation.

        Evaluate the complete movement pattern rather than individual measurements.

        Consider both primary and supporting biomechanical features before selecting a style.

        Step 4 — Select the Best Supported Style

        Choose the movement style that is most strongly supported by the complete biomechanical evidence.

        The selected style should represent the dominant movement pattern observed throughout the corresponding batting phase.

        Step 5 — Generate Explanation

        For every selected style provide:

        Style Meaning
        Biomechanical Reasoning
        Batter-specific Description
        Confidence Score

        The explanation should clearly describe why the selected style best represents the observed biomechanics.

        ANALYSIS GUIDELINES

        While performing the analysis:

        Consider the complete movement pattern instead of isolated feature values.
        Use multiple biomechanical features before selecting a movement style.
        Prioritize consistent movement behaviour over isolated observations.
        Consider both primary and supporting biomechanical evidence.
        Evaluate movement throughout the complete phase instead of individual frames.
        Every conclusion should be directly supported by the provided biomechanical evidence.

        If conflicting evidence exists:

        Select the style supported by the strongest overall evidence.
        Explain the biomechanical reasoning.
        Reduce the confidence score appropriately.

        Never invent movement characteristics that are not supported by the provided inputs.

        CONFIDENCE SCORE

        Every selected movement style must include a confidence score between 0 and 100.

        The confidence score represents how strongly the available biomechanical evidence supports the selected movement style, not how confident the language model feels about its answer.

        Confidence should be estimated using the following principles.

        Increase confidence when:

        Multiple primary biomechanical features independently support the same movement style.
        Supporting biomechanical features reinforce the same conclusion.
        Statistical measurements are internally consistent.
        The movement pattern remains stable throughout the batting phase.
        There is little contradiction between the observed biomechanical features.
        The observed movement closely matches the characteristics described in the Style Documentation.

        Reduce confidence when:

        Primary biomechanical features disagree.
        Supporting features contradict the dominant movement pattern.
        Statistical variability is high.
        Multiple candidate styles appear equally plausible.
        The movement pattern partially matches more than one style.
        The available evidence is weak or incomplete.

        The confidence score should reflect the overall strength, consistency, and quality of the biomechanical evidence rather than the certainty of the prediction.

        OUTPUT REQUIREMENTS

        Return only the JSON defined in the Biomechanical Style Analysis Documentation.

        For every selected movement style provide:

        Selected Style
        Style Meaning
        Biomechanical Reasoning
        Description
        Confidence Score

        Also include:

        Overall Shot Type
        Overall Movement Summary

        Do not invent additional fields.

        Do not modify the JSON structure.

        Do not return markdown, explanations, or commentary outside the JSON.

        FINAL SUMMARY

        The overall summary should combine the findings from every batting phase into a concise biomechanical assessment of the batter.

        The summary should describe:

        Overall batting style
        Lower-body movement strategy
        Body organization
        Weight transfer characteristics
        Rotational behaviour
        Balance and posture
        Stroke execution
        Overall movement efficiency

        The summary should read like a professional batting biomechanics report written by an experienced cricket analyst. It should integrate the observations from all phases into a single coherent description of the batter's movement identity rather than simply listing the selected styles."""
    
    try:
        print("Calling LLM API...")
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
        
        # Check for HTTP errors
        if response.status_code != 200:
            print(f"❌ API Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        response.raise_for_status()
        
        # Parse response
        response_data = response.json()
        
        if 'candidates' not in response_data:
            print(f"❌ Unexpected API response format")
            print(f"Response: {json.dumps(response_data, indent=2)}")
            return False
        
        llm_output = response_data['candidates'][0]['content']['parts'][0]['text']
        llm_output = llm_output.replace("```json", "").replace("```", "").strip()
        
        style_json = output_dir / "style_analysis.json"
        style_json.write_text(llm_output, encoding='utf-8')
        
        print(f"✅ Analysis saved: {style_json}")
        return style_json
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None
    except (KeyError, IndexError) as e:
        print(f"❌ Error parsing API response: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        return None
    except Exception as e:
        print(f"❌ LLM analysis failed: {type(e).__name__}: {e}")
        return None
