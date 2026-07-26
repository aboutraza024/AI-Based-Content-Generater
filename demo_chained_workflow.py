"""
CWT - Complete Chained API Workflow Demo
==========================================
This script demonstrates how the 3 API endpoints connect together sequentially:

  1. POST /api/v1/outline  ---> Generates Editable Outline & Competitor Analysis
  2. POST /api/v1/generate ---> Takes the Confirmed Outline from Step 1 to produce Humanized Content
  3. POST /api/v1/revise   ---> Takes the Content from Step 2 + Feedback to produce Revised Content
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def run_chained_api_workflow():
    print("==================================================================")
    print("STEP 1: Call /api/v1/outline to generate Outline & Competitor Data")
    print("==================================================================")

    step1_input = {
        "language": "English",
        "region": "USA English",
        "content_type": "informational",
        "product_name": "AI Content Writer Pro",
        "tone": "professional",
        "sense": "Explain the benefits of humanized AI writing for professional bloggers",
        "word_count": 600,
        "include_meta": True
    }

    response1 = requests.post(f"{BASE_URL}/api/v1/outline", json=step1_input)
    outline_data = response1.json()

    print("\n✓ STEP 1 RESULT:")
    print("Query Used for Search:", outline_data.get("query_used"))
    print("\nCompetitor Analysis Summary:\n", outline_data.get("competitor_analysis", {}).get("summary"))
    print("\nGenerated Outline Output:\n", outline_data.get("outline"))

    # Extract the generated outline and competitor summary for Step 2
    confirmed_outline = outline_data.get("outline")
    competitor_summary = outline_data.get("competitor_analysis", {}).get("summary")


    print("\n==================================================================")
    print("STEP 2: Pass Confirmed Outline into /api/v1/generate for Full Content")
    print("==================================================================")

    step2_input = {
        "language": step1_input["language"],
        "region": step1_input["region"],
        "content_type": step1_input["content_type"],
        "product_name": step1_input["product_name"],
        "tone": step1_input["tone"],
        "sense": step1_input["sense"],
        "word_count": step1_input["word_count"],
        
        # KEY CONNECTION: Passing output of Step 1 into Step 2!
        "confirmed_outline": confirmed_outline,
        "competitor_summary": competitor_summary,
        "include_meta": True
    }

    response2 = requests.post(f"{BASE_URL}/api/v1/generate", json=step2_input)
    content_data = response2.json()

    print("\n✓ STEP 2 RESULT:")
    print("Word Count Actual:", content_data.get("word_count_actual"))
    print("Linter Clean Status:", content_data.get("lint_report", {}).get("is_clean"))
    print("Linter Violations Fixed:", content_data.get("lint_report", {}).get("violations_found"))
    print("\nMeta Description:", content_data.get("meta_description"))
    print("Meta Tags:", content_data.get("meta_tags"))
    print("\nFinal Humanized Content Output:\n", content_data.get("final_content"))

    # Extract the generated content for Step 3 (Revision)
    previous_content = content_data.get("final_content")


    print("\n==================================================================")
    print("STEP 3: Pass Content & Revision Feedback into /api/v1/revise")
    print("==================================================================")

    step3_input = {
        "language": step1_input["language"],
        "region": step1_input["region"],
        "content_type": step1_input["content_type"],
        "product_name": step1_input["product_name"],
        "tone": step1_input["tone"],
        "sense": step1_input["sense"],
        
        # KEY CONNECTION: Passing output of Step 1 and Step 2 into Step 3!
        "confirmed_outline": confirmed_outline,
        "previous_content": previous_content,
        "revision_feedback": "Add an extra paragraph focusing specifically on SEO benefits and speed.",
        "include_meta": True
    }

    response3 = requests.post(f"{BASE_URL}/api/v1/revise", json=step3_input)
    revised_data = response3.json()

    print("\n✓ STEP 3 RESULT:")
    print("Revised Content Output:\n", revised_data.get("revised_content"))

    print("\n==================================================================")
    print("CHAINED WORKFLOW COMPLETED SUCCESSFULLY!")
    print("==================================================================")

if __name__ == "__main__":
    run_chained_api_workflow()
