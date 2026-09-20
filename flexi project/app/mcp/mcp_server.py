"""
app/mcp/mcp_server.py
Unit 4 — Gradio-based MCP (Model Context Protocol) server.
"""

import os
import sys
import json
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import gradio as gr
from dotenv import load_dotenv

load_dotenv()



def analyze_defect_tool(defect_description: str, session_id: str = "") -> str:
    """
    MCP Tool: Analyze a software defect using AI agents.
    
    Args:
        defect_description: Description of the defect
        session_id: Optional session ID for memory continuity
    
    Returns:
        JSON string with analysis results
    """
    try:
        from app.agents.analysis_agent import analyze_defect
        result = analyze_defect(defect_description, session_id if session_id else None)
        return json.dumps({
            "status": "success",
            "session_id": result["session_id"],
            "analysis": result["response"],
            "tools_used": [t["tool"] for t in result["tool_calls_made"]],
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


def predict_severity_tool(
    component: str,
    error_type: str,
    user_impact: int,
    frequency: int,
    reproducibility: int,
) -> str:
    """
    MCP Tool: Predict defect severity using ML model.
    
    Returns:
        JSON string with severity prediction
    """
    try:
        from app.ml.severity_predictor import predict_severity
        result = predict_severity(
            component=component,
            error_type=error_type,
            user_impact=int(user_impact),
            frequency=int(frequency),
            reproducibility=int(reproducibility),
        )
        return json.dumps({"status": "success", "prediction": result}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


def generate_report_tool(
    defect_description: str,
    analysis: str,
    severity: str,
    component: str,
) -> str:
    """
    MCP Tool: Generate a structured defect report.
    
    Returns:
        JSON string with markdown report
    """
    try:
        from app.agents.reporter_agent import generate_report
        import uuid
        result = generate_report(
            defect_description=defect_description,
            analysis_response=analysis,
            session_id=str(uuid.uuid4())[:8],
            severity=severity,
            component=component,
            send_to_n8n=False,
        )
        return json.dumps({
            "status": "success",
            "defect_id": result["defect_id"],
            "report": result["markdown_report"],
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


def build_mcp_app() -> gr.Blocks:
    """Build the Gradio app that acts as an MCP server."""
    
    with gr.Blocks(title="Defect Reporting MCP Server", theme=gr.themes.Soft()) as app:
        gr.Markdown("""
        # 🔌 AI Defect Reporting — MCP Server
        **Unit 4 Demonstration: Gradio app deployed as MCP-compatible service**
        
        This server exposes 3 tools that external AI agents can call via MCP protocol.
        """)

        with gr.Tab("🔍 analyze_defect"):
            gr.Markdown("**Tool:** `analyze_defect` — Run full AI defect analysis")
            with gr.Row():
                ad_input = gr.Textbox(label="Defect Description", lines=3,
                                      placeholder="Describe the software defect...")
                ad_session = gr.Textbox(label="Session ID (optional)", placeholder="e.g. sess-001")
            ad_btn = gr.Button("Analyze Defect", variant="primary")
            ad_output = gr.Code(language="json", label="MCP Tool Response")
            ad_btn.click(analyze_defect_tool, inputs=[ad_input, ad_session], outputs=ad_output)

        with gr.Tab("🤖 predict_severity"):
            gr.Markdown("**Tool:** `predict_severity` — ML-based severity prediction")
            with gr.Row():
                ps_component = gr.Dropdown(
                    ["Authentication", "Payment", "Database", "API", "Dashboard",
                     "Search", "UI", "Notifications", "Reports", "Settings"],
                    label="Component", value="Authentication"
                )
                ps_error = gr.Dropdown(
                    ["NullPointer", "Crash", "DataCorruption", "SecurityVuln",
                     "Timeout", "ConnectionFail", "ServerError500", "Other"],
                    label="Error Type", value="Crash"
                )
            with gr.Row():
                ps_impact = gr.Slider(1, 5, value=4, step=1, label="User Impact (1-5)")
                ps_freq = gr.Slider(1, 5, value=3, step=1, label="Frequency (1-5)")
                ps_repro = gr.Slider(1, 5, value=4, step=1, label="Reproducibility (1-5)")
            ps_btn = gr.Button("Predict Severity", variant="primary")
            ps_output = gr.Code(language="json", label="MCP Tool Response")
            ps_btn.click(predict_severity_tool,
                         inputs=[ps_component, ps_error, ps_impact, ps_freq, ps_repro],
                         outputs=ps_output)

        with gr.Tab("📝 generate_report"):
            gr.Markdown("**Tool:** `generate_report` — Generate structured defect report")
            with gr.Row():
                gr_defect = gr.Textbox(label="Defect Description", lines=2)
                gr_analysis = gr.Textbox(label="Analysis Summary", lines=2)
            with gr.Row():
                gr_severity = gr.Dropdown(["Low", "Medium", "High", "Critical"],
                                          label="Severity", value="High")
                gr_component = gr.Textbox(label="Component", value="Authentication")
            gr_btn = gr.Button("Generate Report", variant="primary")
            gr_output = gr.Code(language="json", label="MCP Tool Response")
            gr_btn.click(generate_report_tool,
                         inputs=[gr_defect, gr_analysis, gr_severity, gr_component],
                         outputs=gr_output)

        with gr.Tab("📋 MCP Manifest"):
            gr.Markdown("**MCP Tool Manifest** — Clients discover tools via this manifest")
            manifest_btn = gr.Button("Get Tool Manifest")
            manifest_output = gr.Code(language="json", label="MCP Manifest")
            
            def get_manifest():
                return json.dumps({
                    "name": "defect-reporting-mcp-server",
                    "version": "1.0.0",
                    "description": "AI-Based Defect Reporting System — MCP Server",
                    "tools": [
                        {
                            "name": "analyze_defect",
                            "description": "Analyze a software defect using AI agents",
                            "parameters": {
                                "defect_description": "string (required)",
                                "session_id": "string (optional)",
                            }
                        },
                        {
                            "name": "predict_severity",
                            "description": "Predict defect severity using ML model",
                            "parameters": {
                                "component": "string (required)",
                                "error_type": "string (required)",
                                "user_impact": "integer 1-5 (required)",
                                "frequency": "integer 1-5 (required)",
                                "reproducibility": "integer 1-5 (required)",
                            }
                        },
                        {
                            "name": "generate_report",
                            "description": "Generate structured defect report",
                            "parameters": {
                                "defect_description": "string (required)",
                                "analysis": "string (required)",
                                "severity": "Low|Medium|High|Critical (required)",
                                "component": "string (required)",
                            }
                        }
                    ]
                }, indent=2)
            
            manifest_btn.click(get_manifest, outputs=manifest_output)

    return app


if __name__ == "__main__":
    port = int(os.getenv("MCP_PORT", "7861"))
    print(f"Starting MCP Server on port {port}...")
    app = build_mcp_app()
    app.launch(
        server_port=port,
        share=False,
        mcp_server=True,  # Enable MCP server mode
    )
