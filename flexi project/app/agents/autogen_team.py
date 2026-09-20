"""
app/agents/autogen_team.py
Unit 3 — AutoGen multi-model AI agent team.

Three agents discuss the defect collaboratively:
  - Bug Analyst: Technical deep-dive into root cause
  - QA Engineer: Reproducibility and test case design
  - Project Manager: Business impact and priority decision

Uses Gemini directly for simulation since AutoGen's Gemini integration
may require additional config. Falls back to Gemini-powered simulation.
"""

import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-2.5-flash"


def run_autogen_team_discussion(defect_description: str, severity: str = "High") -> str:
    """
    Run an AutoGen-style multi-agent discussion about a defect.

    Three agents discuss the defect and produce a consensus on:
    - Root cause analysis
    - Test cases needed
    - Priority and business impact

    Args:
        defect_description: The defect to analyze
        severity: Pre-assessed severity level

    Returns:
        Full discussion transcript as a string
    """
    try:
        import autogen
        return _run_real_autogen(defect_description, severity)
    except ImportError:
        return _simulate_discussion(defect_description, severity)


def _run_real_autogen(defect_description: str, severity: str) -> str:
    """Run actual AutoGen multi-agent discussion."""
    import autogen

    gemini_config = {
        "config_list": [
            {
                "model": MODEL_NAME,
                "api_key": GEMINI_API_KEY,
                "api_type": "google",
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500,
    }

    bug_analyst = autogen.ConversableAgent(
        name="Bug_Analyst",
        system_message=(
            "You are a Senior Bug Analyst. Analyze the technical root cause, "
            "identify affected code areas, and suggest technical fixes. "
            "Keep responses to 3-4 sentences. Say TERMINATE when done."
        ),
        llm_config=gemini_config,
        human_input_mode="NEVER",
    )

    qa_engineer = autogen.ConversableAgent(
        name="QA_Engineer",
        system_message=(
            "You are a QA Engineer. Design test cases, assess reproducibility "
            "and affected environments, suggest regression tests. "
            "Keep responses to 3-4 sentences. Say TERMINATE when done."
        ),
        llm_config=gemini_config,
        human_input_mode="NEVER",
    )

    project_manager = autogen.ConversableAgent(
        name="Project_Manager",
        system_message=(
            "You are a Project Manager. Assess business impact, prioritize the fix, "
            "identify stakeholders. Keep responses concise. Say TERMINATE when all agents have contributed."
        ),
        llm_config=gemini_config,
        human_input_mode="NEVER",
        is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
    )

    group_chat = autogen.GroupChat(
        agents=[bug_analyst, qa_engineer, project_manager],
        messages=[],
        max_round=6,
        speaker_selection_method="round_robin",
    )
    manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=gemini_config)

    initial_message = (
        f"Team, we have a {severity} severity defect that needs discussion:\n\n"
        f"{defect_description}\n\n"
        "Please analyze this from your respective roles and reach a consensus."
    )

    bug_analyst.initiate_chat(manager, message=initial_message, max_turns=6)

    transcript = ""
    for msg in group_chat.messages:
        if msg.get("content") and msg.get("name"):
            name = msg["name"].replace("_", " ")
            transcript += f"\n**{name}:**\n{msg['content']}\n---\n"

    return transcript if transcript else _simulate_discussion(defect_description, severity)


def _simulate_discussion(defect_description: str, severity: str) -> str:
    """
    Generate a realistic multi-agent discussion using Gemini directly.
    Used when AutoGen is unavailable.
    """
    prompt = (
        f"Simulate a multi-agent discussion between 3 AI agents analyzing this {severity} severity defect:\n\n"
        f'"{defect_description}"\n\n'
        "Format the discussion as a transcript with these 3 agents taking turns:\n"
        "1. Bug Analyst - technical root cause\n"
        "2. QA Engineer - test cases and reproducibility\n"
        "3. Project Manager - business impact and priority\n\n"
        "Each agent should write 3-4 concise sentences. Format each contribution as:\n\n"
        "**[Agent Name]:**\n[Their analysis]\n---\n\n"
        "End with a **Consensus Summary** section."
    )
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        return response.text

    except Exception as e:
        print(f"[AUTOGEN] Gemini failed: {e}. Switching to Groq fallback...")
        try:
            from app.llm_fallback import call_groq_chat
            return call_groq_chat(
                prompt=prompt,
                max_tokens=1200,
            )
        except Exception as groq_err:
            print(f"[AUTOGEN] Groq fallback failed: {groq_err}")
            return (
                f"**Bug Analyst:**\n"
                f"The defect '{defect_description[:80]}' appears to be a critical issue in the core application flow. "
                f"Root cause is likely an unhandled exception or race condition. "
                f"Immediate code review of the relevant module is required.\n---\n\n"
                f"**QA Engineer:**\n"
                f"Test cases should cover normal flow, edge cases, and concurrent user scenarios. "
                f"Reproducibility confirmed at {severity} level. "
                f"Regression tests must be added to the CI/CD pipeline post-fix.\n---\n\n"
                f"**Project Manager:**\n"
                f"This {severity} severity defect impacts user trust and business operations. "
                f"Recommending immediate sprint priority escalation. "
                f"Stakeholders notified.\n---\n\n"
                f"**Consensus Summary:**\n"
                f"The team agrees this is a {severity} priority defect requiring immediate attention. "
                f"Fix estimate: 1-2 business days.\n\n"
                f"*(Note: AI services unavailable — Gemini: {str(e)}, Groq: {str(groq_err)})*"
            )



if __name__ == "__main__":
    transcript = run_autogen_team_discussion(
        "User authentication fails silently — no error shown, user stuck on login page",
        severity="High",
    )
    print(transcript)
