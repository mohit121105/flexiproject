"""
app/agents/triage_agent.py
Unit 2 — Triage agent with guardrail and handoff mechanism.

Responsibilities:
  1. GUARDRAIL: Validate that the input is actually a software defect report
     (rejects off-topic queries like politics, general chat, etc.)
  2. CLASSIFY: Determine defect category and urgency
  3. HANDOFF: Route to appropriate specialist agent (Analysis or Reporter)
"""

import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-2.5-flash"

BLOCKED_TOPICS = ["politics", "religion", "weather", "sports", "recipe", "joke", "cricket", "football"]
VALID_DEFECT_KEYWORDS = [
    "error", "bug", "crash", "fail", "broken", "issue", "problem",
    "exception", "not working", "wrong", "incorrect", "missing",
    "slow", "timeout", "500", "404", "null", "undefined", "fix",
    "defect", "glitch", "unexpected", "unable", "cannot",
]

TRIAGE_SYSTEM_PROMPT = """You are TriageBot, a defect triage agent for a software QA system.

Your ONLY job:
1. Determine if the user input is a valid software defect report
2. If valid: extract key information and classify it
3. If NOT valid: politely redirect the user

Respond with a JSON object ONLY (no markdown, no extra text):
{
  "is_defect": true/false,
  "reason": "why this is or isn't a defect",
  "category": "Authentication|Payment|Database|API|Dashboard|Search|UI|Notifications|Reports|Settings|Other",
  "urgency": "Immediate|High|Normal|Low",
  "summary": "one-line summary of the defect",
  "handoff_to": "analysis_agent|reporter_agent|none",
  "rejection_message": "message to user if not a defect (empty string if valid)"
}

GUARDRAIL RULES:
- Accept: bug reports, error descriptions, system failures, performance issues
- Reject: general questions, off-topic chat (politics, sports, etc.), greetings alone
- Be lenient: if there's any chance it's a defect, accept it
"""


class TriageResult:
    """Structured result from the triage agent."""
    def __init__(self, data: dict):
        self.is_defect: bool = data.get("is_defect", False)
        self.reason: str = data.get("reason", "")
        self.category: str = data.get("category", "Other")
        self.urgency: str = data.get("urgency", "Normal")
        self.summary: str = data.get("summary", "")
        self.handoff_to: str = data.get("handoff_to", "analysis_agent")
        self.rejection_message: str = data.get("rejection_message", "")

    def to_dict(self) -> dict:
        return self.__dict__


def _quick_guardrail_check(text: str) -> bool:
    """Fast keyword-based pre-check before calling LLM."""
    text_lower = text.lower()
    for blocked in BLOCKED_TOPICS:
        if blocked in text_lower and not any(kw in text_lower for kw in VALID_DEFECT_KEYWORDS):
            return False
    return True


def triage_defect(user_input: str) -> TriageResult:
    """
    Run the triage agent on user input.
    Returns TriageResult with classification and routing decision.
    """
    print(f"\n[TRIAGE] Processing: {user_input[:80]}...")

    # Fast keyword guardrail
    if not _quick_guardrail_check(user_input):
        print("[TRIAGE] Blocked by keyword guardrail")
        return TriageResult({
            "is_defect": False,
            "reason": "Input does not appear to be a software defect report",
            "category": "Other",
            "urgency": "Low",
            "summary": "",
            "handoff_to": "none",
            "rejection_message": (
                "I'm specialized in software defect analysis. "
                "Please describe a software bug, error, or system issue you're experiencing."
            ),
        })

    # LLM-based triage
    text = ""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=f"System: {TRIAGE_SYSTEM_PROMPT}\n\nTriage this input:\n\n{user_input}",
        )
        text = response.text.strip()
    except Exception as e:
        print(f"[TRIAGE] Gemini failed: {e}. Switching to Groq fallback...")
        try:
            from app.llm_fallback import call_groq_chat
            text = call_groq_chat(
                prompt=f"Triage this input:\n\n{user_input}",
                system_prompt=TRIAGE_SYSTEM_PROMPT,
                json_mode=True,
            )
        except Exception as groq_err:
            print(f"[TRIAGE] Groq fallback failed: {groq_err}")

    if text:
        try:
            # Strip markdown code blocks if present
            cleaned = text
            if "```" in cleaned:
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
            data = json.loads(cleaned.strip())
            result = TriageResult(data)
            print(f"[TRIAGE] Result: is_defect={result.is_defect}, category={result.category}, urgency={result.urgency}")
            return result
        except json.JSONDecodeError:
            print("[TRIAGE] JSON parse failed, defaulting to accept")

    return TriageResult({
        "is_defect": True,
        "reason": "Accepted by default fallback",
        "category": "Other",
        "urgency": "Normal",
        "summary": user_input[:100],
        "handoff_to": "analysis_agent",
        "rejection_message": "",
    })



if __name__ == "__main__":
    test_inputs = [
        "The payment gateway fails with error 500 after checkout",
        "Tell me about the weather today",
        "User cannot login — getting null pointer exception on submit",
    ]
    for inp in test_inputs:
        result = triage_defect(inp)
        print(f"  is_defect: {result.is_defect}, category: {result.category}")
