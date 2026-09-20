"""
app/tools/n8n_tool.py
Unit 5 — n8n webhook integration tool.

Sends structured defect report data to an n8n webhook, which then
automatically: logs to Google Sheets, emails stakeholders, and
creates a Google Calendar event for the fix review meeting.

If n8n is not running, the tool logs locally and returns a mock confirmation.
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")


def send_defect_to_n8n(
    session_id: str,
    title: str,
    description: str,
    component: str,
    severity: str,
    reporter: str = "AI System",
    report_markdown: str = "",
) -> str:
    """
    Send a defect report to n8n for automated processing.

    n8n workflow will:
      1. Log the defect to Google Sheets
      2. Email the QA team with the report
      3. Create a Google Calendar event for defect review

    Args:
        session_id: Unique session identifier
        title: Defect title/summary
        description: Detailed defect description
        component: Affected software component
        severity: Severity level (Low/Medium/High/Critical)
        reporter: Name of the reporter
        report_markdown: Full markdown report text

    Returns:
        Confirmation message string
    """
    payload = {
        "session_id": session_id,
        "title": title,
        "description": description,
        "component": component,
        "severity": severity,
        "reporter": reporter,
        "report_markdown": report_markdown,
        "timestamp": datetime.utcnow().isoformat(),
        "source": "AI-Based Defect Reporting System",
    }

    if not N8N_WEBHOOK_URL:
        return _log_locally(payload)

    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            timeout=15,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return (
            f"✅ Defect report sent to n8n successfully!\n"
            f"   • Logged to Google Sheets\n"
            f"   • Email notification sent to QA team\n"
            f"   • Calendar event created for defect review\n"
            f"   Status: {response.status_code}"
        )
    except requests.exceptions.ConnectionError:
        return _log_locally(payload, note="n8n not reachable — saved locally")
    except Exception as e:
        return f"⚠️ n8n integration error: {str(e)}\n{_log_locally(payload)}"


def _log_locally(payload: dict, note: str = "n8n not configured") -> str:
    """Save defect data to a local JSON log when n8n is unavailable."""
    log_file = "./defect_reports_log.json"
    try:
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(payload)

        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)

        return (
            f"📋 [{note}] Defect report saved locally to {log_file}\n"
            f"   Title: {payload.get('title')}\n"
            f"   Severity: {payload.get('severity')}\n"
            f"   Component: {payload.get('component')}\n\n"
            f"💡 To enable full automation:\n"
            f"   1. Import n8n/defect_reporting_workflow.json into n8n\n"
            f"   2. Set N8N_WEBHOOK_URL in your .env file\n"
            f"   3. Connect Gmail, Google Sheets & Calendar in n8n"
        )
    except Exception as e:
        return f"Could not save locally: {str(e)}"


def get_n8n_tool_definition() -> dict:
    """Return tool definition for agent function calling."""
    return {
        "name": "send_defect_to_n8n",
        "description": (
            "Send the final defect report to the automation system (n8n). "
            "This triggers: logging to Google Sheets, email notification to QA team, "
            "and Google Calendar event creation for the review meeting."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Short defect title"},
                "description": {"type": "string", "description": "Detailed description"},
                "component": {"type": "string", "description": "Affected component"},
                "severity": {
                    "type": "string",
                    "enum": ["Low", "Medium", "High", "Critical"],
                    "description": "Defect severity level",
                },
                "reporter": {"type": "string", "description": "Who reported the defect"},
                "report_markdown": {"type": "string", "description": "Full report in markdown"},
            },
            "required": ["title", "description", "component", "severity"],
        },
        "function": send_defect_to_n8n,
    }


if __name__ == "__main__":
    result = send_defect_to_n8n(
        session_id="test-001",
        title="Login page crashes on submit",
        description="When user clicks submit on login form, the page throws a 500 error.",
        component="Authentication Module",
        severity="Critical",
        reporter="Test User",
        report_markdown="## Defect Report\n**Severity:** Critical",
    )
    print(result)
