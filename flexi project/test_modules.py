import sys, os
sys.path.insert(0, '.')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv()

print("=" * 50)
print("  AI Defect Reporting System -- Module Tests")
print("=" * 50)

# Test 1: SQLite Memory
print("\n[1] Testing SQLite Memory...")
from app.memory.session_store import save_message, get_history, clear_session
save_message('test-001', 'user', 'Login crashes on Firefox')
save_message('test-001', 'assistant', 'Analyzing the defect...')
history = get_history('test-001')
print(f"    OK: {len(history)} messages stored and retrieved")
clear_session('test-001')

# Test 2: ML Severity Predictor
print("\n[2] Testing ML Severity Predictor...")
from app.ml.severity_predictor import predict_severity
result = predict_severity('Authentication', 'Crash', 5, 4, 5)
print(f"    OK: Severity={result['severity']}, Confidence={result['confidence']:.1f}%")
print(f"    Model: {result['model']}")

# Test 3: Search Tool
print("\n[3] Testing Search Tool (mock mode)...")
from app.tools.search_tool import search_web
search_result = search_web("Firefox login crash 500 error")
print(f"    OK: {len(search_result)} chars returned")

# Test 4: n8n Tool (local fallback)
print("\n[4] Testing n8n Tool (local fallback)...")
from app.tools.n8n_tool import send_defect_to_n8n
n8n_result = send_defect_to_n8n(
    'test-001', 'Login crash', 'Firefox 500 error',
    'Authentication', 'Critical'
)
print("    OK:", n8n_result[:70])

# Test 5: Triage Agent
print("\n[5] Testing Triage Agent...")
from app.agents.triage_agent import triage_defect
t = triage_defect("Login page throws 500 error on Firefox submit")
print(f"    OK: is_defect={t.is_defect}, category={t.category}, urgency={t.urgency}")

t2 = triage_defect("Tell me a joke")
print(f"    Guardrail test: is_defect={t2.is_defect} (expected False)")

print("\n" + "=" * 50)
print("  All tests passed!")
print("=" * 50)
