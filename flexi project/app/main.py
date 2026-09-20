"""
app/main.py
AI-Based Defect Reporting System — Professional Web Application

User-focused UI:
  Tab 1: 🐛 Report & Analyze Defect — Triage, Root-Cause Diagnosis, Severity Scoring, Report Generation
  Tab 2: 👥 Multi-Agent Review      — Collaborative evaluation by Bug Analyst, QA Engineer, and Project Manager
  Tab 3: 📊 Defect History          — Searchable records of all submitted defect reports

Run with: python app/main.py
"""

import os
import sys
import json
import uuid
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
from dotenv import load_dotenv

load_dotenv()

# ── Cached session state ───────────────────────────────────────────────────────
_current_session = {"id": str(uuid.uuid4())[:8], "last_result": None}


# ── Tab 1: Full defect reporting pipeline ──────────────────────────────────────
def submit_defect(defect_text: str, progress=gr.Progress()):
    """Run the complete defect processing pipeline: Triage -> Analyze -> Predict -> Report."""
    if not defect_text.strip():
        return (
            "⚠️ Please describe the defect you encountered.",
            "",
            "",
            "",
            "",
        )

    session_id = _current_session["id"]
    steps_log = []

    progress(0.1, desc="🔍 Validating defect submission...")
    steps_log.append("### 1. Defect Triage & Guardrail")

    triage = None
    triage_category = "Other"
    try:
        from app.agents.triage_agent import triage_defect
        triage = triage_defect(defect_text)
        steps_log.append(f"- **Valid Defect:** {'Yes' if triage.is_defect else 'No'}")
        steps_log.append(f"- **Identified Category:** `{triage.category}`")
        steps_log.append(f"- **Urgency Assessment:** `{triage.urgency}`")

        if not triage.is_defect:
            return (
                f"⛔ **Submission Rejected by Quality Guardrail**\n\n{triage.rejection_message}",
                "Not applicable",
                "Not applicable",
                "\n".join(steps_log),
                "",
            )
        triage_category = triage.category
    except Exception as e:
        steps_log.append(f"- *Triage Note:* {str(e)}")
        triage_category = "Other"

    progress(0.35, desc="🧠 Running root-cause analysis...")
    steps_log.append("\n### 2. AI Root-Cause Diagnosis")

    analysis_response = ""
    tools_used = []
    try:
        from app.agents.analysis_agent import analyze_defect
        analysis = analyze_defect(defect_text, session_id)
        analysis_response = analysis["response"]
        tools_used = [t["tool"] for t in analysis.get("tool_calls_made", [])]
        if tools_used:
            steps_log.append(f"- **Diagnostic Tools Used:** `{', '.join(tools_used)}`")
        steps_log.append(f"- **Context Memory Entries:** {analysis.get('history_length', 0)}")
    except Exception as e:
        analysis_response = f"Analysis error: {str(e)}"
        steps_log.append(f"- *Analysis Error:* {str(e)}")

    progress(0.60, desc="🤖 Calculating severity score...")
    steps_log.append("\n### 3. Machine Learning Severity Assessment")

    severity = "Medium"
    try:
        from app.ml.severity_predictor import predict_severity
        desc_lower = defect_text.lower()
        error_type = ("Crash" if "crash" in desc_lower else
                      "Timeout" if "timeout" in desc_lower else
                      "NullPointer" if "null" in desc_lower else
                      "ServerError500" if "500" in desc_lower else "Other")
        user_impact = 4 if (triage and getattr(triage, "urgency", "") in ["Immediate", "High"]) else 3
        prediction = predict_severity(
            component=triage_category,
            error_type=error_type,
            user_impact=user_impact,
            frequency=3,
            reproducibility=3,
        )
        severity = prediction["severity"]
        conf = prediction.get("confidence", 0)
        steps_log.append(f"- **Predicted Severity:** {prediction['icon']} **{severity}**")
        steps_log.append(f"- **Confidence:** `{conf:.1f}%` ({prediction.get('model', 'Statistical ML')})")
    except Exception as e:
        steps_log.append(f"- *Severity Predictor Error:* {str(e)}")

    progress(0.85, desc="📝 Generating standardized report...")
    steps_log.append("\n### 4. Report Generation & Notification")

    markdown_report = ""
    n8n_status = ""
    try:
        from app.agents.reporter_agent import generate_report
        report = generate_report(
            defect_description=defect_text,
            analysis_response=analysis_response,
            session_id=session_id,
            severity=severity,
            component=triage_category,
            send_to_n8n=True,
        )
        markdown_report = report["markdown_report"]
        n8n_status = report["n8n_status"]
        steps_log.append(f"- **Defect Tracking ID:** `{report['defect_id']}`")
        if "saved locally" in n8n_status:
            steps_log.append("- **Notification Status:** Logged to local database")
        else:
            steps_log.append("- **Notification Status:** Dispatched via automated webhook")
    except Exception as e:
        markdown_report = f"Report generation error: {str(e)}"
        steps_log.append(f"- *Report Error:* {str(e)}")

    _current_session["last_result"] = {
        "severity": severity,
        "component": triage_category,
        "defect_text": defect_text,
        "report": markdown_report,
    }

    progress(1.0, desc="✅ Analysis complete!")

    severity_display = {
        "Critical": "🔴 **CRITICAL**",
        "High": "🟠 **HIGH**",
        "Medium": "🟡 **MEDIUM**",
        "Low": "🟢 **LOW**",
    }.get(severity, severity)

    return (
        analysis_response,
        severity_display,
        triage_category,
        "\n".join(steps_log),
        markdown_report,
    )


# ── Tab 2: Multi-agent bug review ─────────────────────────────────────────────
def run_team_discussion(defect_text: str, progress=gr.Progress()):
    """Run collaborative multi-agent discussion on a bug."""
    if not defect_text.strip():
        # Fall back to last analyzed defect if available
        last_defect = (_current_session.get("last_result") or {}).get("defect_text", "")
        if last_defect:
            defect_text = last_defect
        else:
            return "⚠️ Please enter a defect description to initiate team discussion."

    severity = (_current_session.get("last_result") or {}).get("severity", "High")
    progress(0.3, desc="👥 Convening specialist review team...")
    try:
        from app.agents.autogen_team import run_autogen_team_discussion
        result = run_autogen_team_discussion(defect_text, severity)
        return result
    except Exception as e:
        return f"Team discussion error: {str(e)}"


# ── Tab 3: Defect history ──────────────────────────────────────────────────────
def load_history():
    """Load all recorded defect reports from SQLite."""
    try:
        from app.memory.session_store import get_all_defect_reports
        reports = get_all_defect_reports()
        if not reports:
            return "📭 No defect reports recorded yet. Submit an issue to populate records."

        rows = []
        for r in reports[:30]:
            title = str(r.get('title', ''))[:45].replace("|", "-")
            component = str(r.get('component', 'N/A')).replace("|", "-")
            severity = str(r.get('severity', 'N/A'))
            date = str(r.get('created_at', ''))[:16]
            session = str(r.get('session_id', 'N/A'))
            rows.append(f"| `{session}` | {title} | `{component}` | **{severity}** | {date} |")

        table = (
            "| Tracking Session | Summary | Component | Severity | Logged Date |\n"
            "|:---|:---|:---|:---|:---|\n"
            + "\n".join(rows)
        )
        return f"### 📋 Logged Defects ({len(reports)} total)\n\n{table}"
    except Exception as e:
        return f"Error loading history: {str(e)}"


# ── Session management ─────────────────────────────────────────────────────────
def new_session():
    _current_session["id"] = str(uuid.uuid4())[:8]
    _current_session["last_result"] = None
    return f"Active Session: `{_current_session['id']}`"


# ── Build Gradio Application ───────────────────────────────────────────────────
def build_app() -> gr.Blocks:

    with gr.Blocks(
        title="AI Defect Reporting & Triage System",
        theme=gr.themes.Soft(primary_hue="blue", neutral_hue="slate"),
        css="""
        .main-header {
            text-align: center;
            padding: 16px 10px;
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-radius: 12px;
            color: #f8fafc;
            margin-bottom: 20px;
        }
        .main-header h1 {
            font-size: 26px;
            font-weight: 700;
            margin-bottom: 6px;
            color: #f8fafc;
        }
        .main-header p {
            font-size: 14px;
            color: #94a3b8;
            margin: 0;
        }
        .metric-card {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px;
        }
        """
    ) as app:

        # ── Header ─────────────────────────────────────────────────────────────
        gr.HTML("""
        <div class='main-header'>
          <h1>🐛 AI Defect Reporting & Triage System</h1>
          <p>Automated defect validation, intelligent root-cause diagnosis, ML severity scoring, and standardized reporting.</p>
        </div>
        """)

        with gr.Row():
            session_label = gr.Markdown(f"Active Session: `{_current_session['id']}`")
            new_session_btn = gr.Button("🔄 Start Fresh Session", size="sm", scale=0)

        new_session_btn.click(new_session, outputs=session_label)

        # ── TAB 1: Report & Analyze Defect ─────────────────────────────────────
        with gr.Tab("🐛 Report & Analyze Defect"):
            gr.Markdown(
                "Describe the software bug or unexpected behavior below. The AI pipeline will automatically validate the issue, "
                "investigate root causes, predict severity with ML, and generate a standardized defect report."
            )

            with gr.Row():
                defect_input = gr.Textbox(
                    label="Defect Description",
                    placeholder="Describe what happened, expected behavior, affected browser/device, or error messages...",
                    lines=4,
                    scale=3,
                )
                with gr.Column(scale=1):
                    submit_btn = gr.Button("🚀 Analyze Defect", variant="primary", size="lg")
                    gr.Markdown("<small>⚡ Performs automated triage, root-cause diagnosis & severity assessment</small>")

            with gr.Row():
                severity_out = gr.Markdown(label="Assessed Severity")
                component_out = gr.Textbox(label="Identified Component", interactive=False)

            with gr.Row():
                with gr.Column(scale=1):
                    analysis_out = gr.Textbox(
                        label="🧠 Root-Cause & Technical Diagnosis",
                        lines=12,
                        interactive=False,
                    )
                with gr.Column(scale=1):
                    steps_out = gr.Markdown(label="📋 Processing Pipeline Trace")

            report_out = gr.Markdown(label="📄 Generated Defect Report")

            submit_btn.click(
                submit_defect,
                inputs=[defect_input],
                outputs=[analysis_out, severity_out, component_out, steps_out, report_out],
            )

            gr.Examples(
                examples=[
                    ["When users upload a profile photo larger than 10MB, the image processing worker crashes with an OutOfMemoryError, causing all subsequent registrations to time out with 504."],
                    ["In the notification settings page, rapidly toggling the email digest switch causes the toggle state to desync from the server, leaving the save button disabled."],
                    ["The payment checkout button becomes unresponsive on Safari iOS 17 during 3D Secure verification redirect."],
                    ["Search results display incorrect pricing when filtering items by descending discount percentage."],
                    ["Can you write a poem about the sunrise?"],  # Quality Guardrail will politely reject this
                ],
                inputs=defect_input,
                label="Quick Sample Issues (Click to populate)",
            )

        # ── TAB 2: Multi-Agent Bug Review ──────────────────────────────────────
        with gr.Tab("👥 Multi-Agent Bug Review"):
            gr.Markdown(
                "Convene an automated cross-functional review meeting. Three specialized AI roles evaluate the defect from their perspective: "
                "**Bug Analyst** (architecture & root cause), **QA Engineer** (reproducibility & test design), and **Project Manager** (business impact & priority)."
            )

            autogen_input = gr.Textbox(
                label="Defect to Review",
                placeholder="Enter a defect description (or leave empty to evaluate the issue submitted in Tab 1)...",
                lines=3,
            )
            autogen_btn = gr.Button("🗣️ Convene Expert Review Team", variant="primary")
            autogen_out = gr.Markdown(label="Team Review Transcript & Consensus")

            autogen_btn.click(run_team_discussion, inputs=[autogen_input], outputs=[autogen_out])

        # ── TAB 3: Defect History & Records ────────────────────────────────────
        with gr.Tab("📋 Defect History & Records"):
            gr.Markdown(
                "View all past defects submitted through the system. Records are stored persistently in the database."
            )

            refresh_btn = gr.Button("🔄 Refresh Records", variant="secondary")
            history_out = gr.Markdown(label="Logged Defect Records")

            refresh_btn.click(load_history, outputs=[history_out])
            app.load(load_history, outputs=[history_out])

    return app


def find_available_port(preferred_port: int, max_range: int = 50) -> int:
    """Find the preferred port or the next available port if preferred is in use."""
    import socket
    for p in range(preferred_port, preferred_port + max_range):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    return preferred_port


if __name__ == "__main__":
    target_port = int(os.getenv("APP_PORT", "7860"))
    port = find_available_port(target_port)
    if port != target_port:
        print(f"⚠️ Port {target_port} is busy. Automatically switched to port {port}.")

    print("=" * 60)
    print("   AI Defect Reporting & Triage System")
    print(f"   Running on http://localhost:{port}")
    print("=" * 60)

    # Train ML model if not already trained
    model_path = os.getenv("MODEL_PATH", "./app/ml/severity_model.joblib")
    if not os.path.exists(model_path):
        print("Training ML model...")
        try:
            import subprocess
            subprocess.run([sys.executable, "app/ml/train_model.py"], check=True)
        except Exception as e:
            print(f"Model training note: {e}")

    share_mode = "--share" in sys.argv or os.getenv("GRADIO_SHARE", "false").lower() in ("true", "1", "yes")
    app = build_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=share_mode,
        show_error=True,
    )

