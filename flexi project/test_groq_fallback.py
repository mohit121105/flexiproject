"""
test_groq_fallback.py
Verifies Groq fallback triggers correctly when Gemini is forced to fail.
"""
import sys, os
sys.path.insert(0, '.')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv()

import unittest.mock as mock

print("=" * 60)
print("  Groq Fallback Integration Tests")
print("=" * 60)

# ── Test 1: llm_fallback module directly ──────────────────────────
print("\n[1] Direct Groq call (llm_fallback.py)...")
try:
    from app.llm_fallback import call_groq_chat
    result = call_groq_chat(
        prompt="In one sentence, what is a 500 Internal Server Error?",
        system_prompt="You are a concise technical expert.",
    )
    print(f"    OK: {result[:120]}")
except Exception as e:
    print(f"    FAIL: {e}")

# ── Test 2: Triage Agent with forced Gemini failure ───────────────
print("\n[2] Triage Agent — Groq fallback when Gemini fails...")
try:
    import google.genai as genai_module

    # Patch Gemini to raise an exception
    with mock.patch.object(genai_module.Client, '__init__', side_effect=Exception("Simulated Gemini API quota exceeded")):
        from app.agents.triage_agent import triage_defect
        result = triage_defect("The dashboard crashes when more than 50 widgets are loaded simultaneously.")
        print(f"    OK via Groq: is_defect={result.is_defect}, category={result.category}")
except Exception as e:
    print(f"    FAIL: {e}")

# ── Test 3: Reporter Agent with forced Gemini failure ─────────────
print("\n[3] Reporter Agent — Groq fallback when Gemini fails...")
try:
    with mock.patch.object(genai_module.Client, '__init__', side_effect=Exception("Simulated Gemini API quota exceeded")):
        from app.agents.reporter_agent import generate_report
        result = generate_report(
            defect_description="Dashboard crashes on 50+ widgets",
            analysis_response="Root cause: memory overflow in widget renderer",
            session_id="groq-test-01",
            severity="High",
            component="Dashboard",
            send_to_n8n=False,
        )
        has_report = len(result["markdown_report"]) > 50
        print(f"    OK via Groq: defect_id={result['defect_id']}, report_length={len(result['markdown_report'])} chars")
        print(f"    Report preview: {result['markdown_report'][:120]}...")
except Exception as e:
    print(f"    FAIL: {e}")

# ── Test 4: AutoGen discussion with forced Gemini failure ─────────
print("\n[4] AutoGen Team — Groq fallback when Gemini fails...")
try:
    with mock.patch.object(genai_module.Client, '__init__', side_effect=Exception("Simulated Gemini API quota exceeded")):
        from app.agents.autogen_team import run_autogen_team_discussion
        result = run_autogen_team_discussion("Dashboard crashes on 50+ widgets", "High")
        print(f"    OK via Groq: {len(result)} chars")
        print(f"    Preview: {result[:150]}...")
except Exception as e:
    print(f"    FAIL: {e}")

print("\n" + "=" * 60)
print("  Groq Fallback Tests Complete!")
print("=" * 60)
