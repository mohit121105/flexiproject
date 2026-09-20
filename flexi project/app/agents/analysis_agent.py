"""
app/agents/analysis_agent.py
Unit 1 — Core Gemini-based defect analysis agent.

Features (per syllabus Unit 1):
  - Built with Google Gemini API (new google.genai SDK)
  - SQLite-based persistent session memory for multi-turn queries
  - Integrated tools: web search (Tavily/mock) + ML severity predictor
  - Tracing: prints agent reasoning steps to console/logs
"""

import os
import json
import uuid
from google import genai
from google.genai import types
from dotenv import load_dotenv

from app.memory.session_store import save_message, get_history
from app.tools.search_tool import search_web
from app.ml.severity_predictor import predict_severity

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-2.5-flash"

SYSTEM_PROMPT = """You are DefectAnalyst, an expert AI agent specializing in software defect analysis.

Your role:
1. Analyze software defect reports submitted by users
2. Ask clarifying questions if the defect is unclear
3. Use the search_web tool to find known issues, fixes, or related bugs
4. Use the predict_severity tool to assess defect severity using ML
5. Provide structured analysis including: root cause hypothesis, impact assessment, and suggested fix

Always be professional, thorough, and evidence-based.
"""

# Tool declarations for Gemini function calling
TOOLS = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="search_web",
                description="Search the internet for information about a software defect, error, or known fix.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "query": types.Schema(
                            type="STRING",
                            description="Search query for finding defect-related information",
                        ),
                    },
                    required=["query"],
                ),
            ),
            types.FunctionDeclaration(
                name="predict_severity",
                description="Predict defect severity using ML model. Returns Low/Medium/High/Critical with confidence.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "component": types.Schema(
                            type="STRING",
                            description="Affected component e.g. Authentication, Payment, API, Database, UI",
                        ),
                        "error_type": types.Schema(
                            type="STRING",
                            description="Type of error e.g. NullPointer, Crash, Timeout, ServerError500",
                        ),
                        "user_impact": types.Schema(
                            type="INTEGER",
                            description="User impact 1-5 (1=minimal, 5=all users affected)",
                        ),
                        "frequency": types.Schema(
                            type="INTEGER",
                            description="Frequency 1-5 (1=rare, 5=always occurs)",
                        ),
                        "reproducibility": types.Schema(
                            type="INTEGER",
                            description="Reproducibility 1-5 (1=hard, 5=always reproducible)",
                        ),
                    },
                    required=["component", "error_type", "user_impact", "frequency", "reproducibility"],
                ),
            ),
        ]
    )
]

TOOL_FUNCTIONS = {
    "search_web": lambda query: search_web(query),
    "predict_severity": lambda **kwargs: json.dumps(predict_severity(**kwargs), indent=2),
}


def _execute_tool(tool_name: str, tool_args: dict) -> str:
    """Execute a tool call and return its result as a string."""
    if tool_name not in TOOL_FUNCTIONS:
        return f"Unknown tool: {tool_name}"
    try:
        if tool_name == "predict_severity":
            result = TOOL_FUNCTIONS[tool_name](**tool_args)
        else:
            result = TOOL_FUNCTIONS[tool_name](**tool_args)
        return str(result) if not isinstance(result, str) else result
    except Exception as e:
        return f"Tool error: {str(e)}"


def analyze_defect(user_message: str, session_id: str = None) -> dict:
    """
    Run the defect analysis agent on a user message.

    Args:
        user_message: The defect description from the user
        session_id: Session ID for persistent memory (creates new if None)

    Returns:
        dict with keys: session_id, response, tool_calls_made, history_length
    """
    if not session_id:
        session_id = str(uuid.uuid4())[:8]

    print(f"\n[TRACE] Session: {session_id} | Analyzing: {user_message[:80]}...")

    # Load conversation history from SQLite
    history = get_history(session_id, limit=10)

    # Build contents list for Gemini (new SDK format)
    contents = []
    for h in history:
        role = "user" if h["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=h["content"])]))

    # Add current user message
    contents.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

    # Save user message to memory
    save_message(session_id, "user", user_message)

    client = genai.Client(api_key=GEMINI_API_KEY)
    tool_calls_made = []
    final_response = ""

    try:
        max_iterations = 5
        for iteration in range(max_iterations):
            print(f"[TRACE] Iteration {iteration + 1}/{max_iterations}")

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=TOOLS,
                ),
            )

            candidate = response.candidates[0]
            has_tool_call = False

            # Check all parts for function calls
            for part in candidate.content.parts:
                if part.function_call:
                    has_tool_call = True
                    fn_name = part.function_call.name
                    fn_args = dict(part.function_call.args)

                    print(f"[TRACE] Tool call: {fn_name}({fn_args})")
                    tool_result = _execute_tool(fn_name, fn_args)
                    print(f"[TRACE] Tool result: {tool_result[:100]}...")

                    tool_calls_made.append({
                        "tool": fn_name,
                        "args": fn_args,
                        "result_preview": tool_result[:200],
                    })

                    # Add model turn with function call
                    contents.append(candidate.content)
                    # Add tool result turn
                    contents.append(
                        types.Content(
                            role="user",
                            parts=[
                                types.Part(
                                    function_response=types.FunctionResponse(
                                        name=fn_name,
                                        response={"result": tool_result},
                                    )
                                )
                            ],
                        )
                    )
                    break  # process one tool call per iteration

            if not has_tool_call:
                # Extract text response
                for part in candidate.content.parts:
                    if part.text:
                        final_response += part.text
                break

        if not final_response:
            final_response = "Analysis complete. Please check the tool results above."

    except Exception as e:
        print(f"[TRACE] Gemini failed: {e}. Switching to Groq fallback...")
        try:
            from app.llm_fallback import call_groq_chat
            # Build a plain text history summary for Groq (no function-calling needed)
            history_text = ""
            for h in history:
                history_text += f"[{h['role']}]: {h['content']}\n"

            groq_prompt = (
                f"You are a software defect analysis expert.\n"
                f"Previous conversation:\n{history_text}\n"
                f"Current defect description:\n{user_message}\n\n"
                f"Provide a detailed technical analysis: root cause hypothesis, "
                f"affected components, steps to reproduce, and recommended fix."
            )
            final_response = call_groq_chat(
                prompt=groq_prompt,
                system_prompt=SYSTEM_PROMPT,
                max_tokens=1200,
            )
            print("[TRACE] Groq fallback analysis succeeded.")
        except Exception as groq_err:
            print(f"[TRACE] Groq fallback failed: {groq_err}")
            final_response = (
                f"Unable to complete analysis (Gemini: {str(e)}, Groq: {str(groq_err)}).\n"
                "Please check your API keys in .env and try again."
            )

    save_message(session_id, "assistant", final_response)
    print(f"[TRACE] Response saved. History length: {len(history) + 2}")


    return {
        "session_id": session_id,
        "response": final_response,
        "tool_calls_made": tool_calls_made,
        "history_length": len(history) + 2,
    }


if __name__ == "__main__":
    result = analyze_defect("The login page crashes with a 500 error when users submit the form on Firefox.")
    print(f"\nSession: {result['session_id']}")
    print(f"Tools: {[t['tool'] for t in result['tool_calls_made']]}")
    print(f"\nResponse:\n{result['response']}")
