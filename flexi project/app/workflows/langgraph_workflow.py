"""
app/workflows/langgraph_workflow.py
Unit 3 — LangGraph stateful agentic workflow.
"""

import os
import json
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from typing import TypedDict, Literal
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-2.5-flash"



# ── State definition ───────────────────────────────────────────────────────────
class DefectState(TypedDict):
    """State object passed between LangGraph nodes."""
    user_input: str
    session_id: str
    is_valid_defect: bool
    triage_category: str
    triage_urgency: str
    analysis_response: str
    severity: str
    component: str
    confidence: float
    report_markdown: str
    n8n_status: str
    current_step: str
    error: str


def build_workflow():
    """
    Build and compile the LangGraph defect processing workflow.
    Returns compiled graph or None if LangGraph unavailable.
    """
    try:
        from langgraph.graph import StateGraph, END
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage, SystemMessage
    except ImportError as e:
        print(f"[LANGGRAPH] Import error: {e}")
        return None

    # ── Node functions ─────────────────────────────────────────────────────────

    def node_triage(state: DefectState) -> DefectState:
        """Node 1: Triage — validate and classify the defect."""
        print(f"[LANGGRAPH] Node: triage | Input: {state['user_input'][:50]}")
        try:
            from app.agents.triage_agent import triage_defect
            result = triage_defect(state["user_input"])
            return {
                **state,
                "is_valid_defect": result.is_defect,
                "triage_category": result.category,
                "triage_urgency": result.urgency,
                "current_step": "triage_complete",
                "error": "" if result.is_defect else result.rejection_message,
            }
        except Exception as e:
            return {**state, "is_valid_defect": True, "triage_category": "Other",
                    "triage_urgency": "Normal", "current_step": "triage_error", "error": str(e)}

    def node_analyze(state: DefectState) -> DefectState:
        """Node 2: Analysis — deep defect analysis with Gemini + tools."""
        print(f"[LANGGRAPH] Node: analyze")
        try:
            from app.agents.analysis_agent import analyze_defect
            result = analyze_defect(state["user_input"], state["session_id"])
            return {
                **state,
                "analysis_response": result["response"],
                "session_id": result["session_id"],
                "current_step": "analysis_complete",
            }
        except Exception as e:
            return {**state, "analysis_response": f"Analysis error: {str(e)}",
                    "current_step": "analysis_error"}

    def node_predict_severity(state: DefectState) -> DefectState:
        """Node 3: ML severity prediction."""
        print(f"[LANGGRAPH] Node: predict_severity")
        try:
            from app.ml.severity_predictor import predict_severity

            # Map triage category to component
            component = state.get("triage_category", "Other")
            # Infer error type from description
            desc = state["user_input"].lower()
            error_type = "Crash" if "crash" in desc else \
                         "Timeout" if "timeout" in desc else \
                         "NullPointer" if "null" in desc else \
                         "ServerError500" if "500" in desc else "Other"

            urgency_to_impact = {"Immediate": 5, "High": 4, "Normal": 3, "Low": 2}
            user_impact = urgency_to_impact.get(state.get("triage_urgency", "Normal"), 3)

            prediction = predict_severity(
                component=component,
                error_type=error_type,
                user_impact=user_impact,
                frequency=3,
                reproducibility=3,
            )

            return {
                **state,
                "severity": prediction["severity"],
                "component": component,
                "confidence": prediction.get("confidence", 0),
                "current_step": "severity_predicted",
            }
        except Exception as e:
            return {**state, "severity": "Medium", "component": "Unknown",
                    "confidence": 0.0, "current_step": "severity_error"}

    def node_generate_report(state: DefectState) -> DefectState:
        """Node 4: Generate final structured report."""
        print(f"[LANGGRAPH] Node: generate_report")
        try:
            from app.agents.reporter_agent import generate_report
            result = generate_report(
                defect_description=state["user_input"],
                analysis_response=state["analysis_response"],
                session_id=state["session_id"],
                severity=state["severity"],
                component=state["component"],
                send_to_n8n=True,
            )
            return {
                **state,
                "report_markdown": result["markdown_report"],
                "n8n_status": result["n8n_status"],
                "current_step": "report_generated",
            }
        except Exception as e:
            return {**state, "report_markdown": f"Report generation error: {str(e)}",
                    "current_step": "report_error"}

    def node_reject(state: DefectState) -> DefectState:
        """Node for rejected inputs (not defects)."""
        print(f"[LANGGRAPH] Node: reject")
        return {
            **state,
            "report_markdown": f"⛔ **Not a defect report**\n\n{state.get('error', 'Please submit a software defect.')}",
            "current_step": "rejected",
        }

    def route_after_triage(state: DefectState) -> Literal["analyze", "reject"]:
        """Routing function: after triage, go to analyze or reject."""
        return "analyze" if state.get("is_valid_defect", False) else "reject"

    # ── Build graph ────────────────────────────────────────────────────────────
    workflow = StateGraph(DefectState)

    workflow.add_node("triage", node_triage)
    workflow.add_node("analyze", node_analyze)
    workflow.add_node("predict_severity", node_predict_severity)
    workflow.add_node("generate_report", node_generate_report)
    workflow.add_node("reject", node_reject)

    workflow.set_entry_point("triage")

    workflow.add_conditional_edges(
        "triage",
        route_after_triage,
        {"analyze": "analyze", "reject": "reject"},
    )
    workflow.add_edge("analyze", "predict_severity")
    workflow.add_edge("predict_severity", "generate_report")
    workflow.add_edge("generate_report", END)
    workflow.add_edge("reject", END)

    return workflow.compile()


def run_workflow(user_input: str, session_id: str = None) -> DefectState:
    """
    Execute the full LangGraph defect processing workflow.
    
    Falls back to direct agent pipeline if LangGraph unavailable.
    """
    import uuid
    if not session_id:
        session_id = str(uuid.uuid4())[:8]

    initial_state = DefectState(
        user_input=user_input,
        session_id=session_id,
        is_valid_defect=False,
        triage_category="",
        triage_urgency="",
        analysis_response="",
        severity="",
        component="",
        confidence=0.0,
        report_markdown="",
        n8n_status="",
        current_step="started",
        error="",
    )

    graph = build_workflow()
    if graph is None:
        # Fallback: run agents directly
        return _run_fallback_pipeline(initial_state)

    print(f"\n[LANGGRAPH] Starting workflow for session {session_id}...")
    final_state = graph.invoke(initial_state)
    print(f"[LANGGRAPH] Workflow complete: {final_state.get('current_step')}")
    return final_state


def _run_fallback_pipeline(state: DefectState) -> DefectState:
    """Direct agent pipeline when LangGraph is unavailable."""
    print("[LANGGRAPH] Using direct fallback pipeline...")
    
    from app.agents.triage_agent import triage_defect
    from app.agents.analysis_agent import analyze_defect
    from app.ml.severity_predictor import predict_severity
    from app.agents.reporter_agent import generate_report

    triage = triage_defect(state["user_input"])
    state["is_valid_defect"] = triage.is_defect
    state["triage_category"] = triage.category
    state["triage_urgency"] = triage.urgency

    if not triage.is_defect:
        state["report_markdown"] = f"⛔ {triage.rejection_message}"
        state["current_step"] = "rejected"
        return state

    analysis = analyze_defect(state["user_input"], state["session_id"])
    state["analysis_response"] = analysis["response"]
    state["session_id"] = analysis["session_id"]

    prediction = predict_severity(
        component=triage.category,
        error_type="Other",
        user_impact=4,
        frequency=3,
        reproducibility=3,
    )
    state["severity"] = prediction["severity"]
    state["component"] = triage.category

    report = generate_report(
        defect_description=state["user_input"],
        analysis_response=state["analysis_response"],
        session_id=state["session_id"],
        severity=state["severity"],
        component=state["component"],
        send_to_n8n=True,
    )
    state["report_markdown"] = report["markdown_report"]
    state["n8n_status"] = report["n8n_status"]
    state["current_step"] = "report_generated"
    return state


if __name__ == "__main__":
    result = run_workflow("The checkout button does nothing when clicked on mobile Safari")
    print(f"\n{'='*60}")
    print(f"Step: {result['current_step']}")
    print(f"Severity: {result['severity']}")
    print(f"\nReport Preview:\n{result['report_markdown'][:500]}")
