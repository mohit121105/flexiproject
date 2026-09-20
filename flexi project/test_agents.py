import sys, os
sys.path.insert(0, '.')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv()

print("=" * 55)
print("  AI Defect Reporting System -- Full Agent Tests")
print("=" * 55)

# Test 1: Triage Agent
print("\n[1] Testing Triage Agent (gemini-2.5-flash)...")
try:
    from app.agents.triage_agent import triage_defect
    t = triage_defect("Login page crashes with 500 error on Firefox submit")
    print(f"    OK: is_defect={t.is_defect}, category={t.category}, urgency={t.urgency}")
    t2 = triage_defect("Tell me a joke")
    print(f"    Guardrail OK: is_defect={t2.is_defect}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 2: Analysis Agent
print("\n[2] Testing Analysis Agent (with tool calling)...")
try:
    from app.agents.analysis_agent import analyze_defect
    result = analyze_defect("Payment button does nothing on Safari iOS", "test-full-001")
    print(f"    OK: session={result['session_id']}, tools_used={[t['tool'] for t in result['tool_calls_made']]}")
    print(f"    Response preview: {result['response'][:150]}...")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 3: Reporter Agent
print("\n[3] Testing Reporter Agent...")
try:
    from app.agents.reporter_agent import generate_report
    report = generate_report(
        defect_description="Payment button unresponsive on Safari iOS",
        analysis_response="Root cause: webkit event handler bug. Impact: all iOS users.",
        session_id="test-full-001",
        severity="High",
        component="Payment",
        send_to_n8n=True,
    )
    print(f"    OK: defect_id={report['defect_id']}")
    print(f"    Report preview: {report['markdown_report'][:150]}...")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 4: AutoGen Team
print("\n[4] Testing AutoGen Team Discussion...")
try:
    from app.agents.autogen_team import run_autogen_team_discussion
    transcript = run_autogen_team_discussion(
        "Database connection pool exhausted under load", "Critical"
    )
    print(f"    OK: transcript length={len(transcript)} chars")
    print(f"    Preview: {transcript[:200]}...")
except Exception as e:
    print(f"    ERROR: {e}")

print("\n" + "=" * 55)
print("  Agent Tests Complete!")
print("=" * 55)
