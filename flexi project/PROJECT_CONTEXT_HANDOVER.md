# Project Context & Handover Document: AI-Based Defect Reporting System

**Course:** Agentic AI & Automation — Symbiosis International University  
**Project Title:** AI-Based Defect Reporting System  
**Project Root:** `E:\flexi project`  
**Last Updated:** September 20, 2026  
**Status:** ✅ Fully Built, Verified, and Running with Dual-LLM Fallback  

---

## 1. Executive Summary & Objective

Build an end-to-end **AI-Based Defect Reporting System** covering all 5 units of the *Agentic AI & Automation* syllabus:

- **Unit 1:** Single Gemini Agent + SQLite memory + Tavily web search tool + tracing
- **Unit 2:** Triage Agent (guardrail + handoff) → Analysis Agent → Reporter Agent
- **Unit 3:** AutoGen multi-agent collaborative discussion + LangGraph StateGraph workflow
- **Unit 4:** CrewAI crew (EDA + ML) + Random Forest severity predictor + Gradio MCP server
- **Unit 5:** n8n webhook automation → Google Sheets + Gmail + Google Calendar

---

## 2. Environment & Configuration

| Setting | Value |
|---|---|
| **OS** | Windows (PowerShell) |
| **Python** | 3.13 |
| **Primary LLM SDK** | `google-genai` v2.16.0 |
| **Primary Model** | `gemini-2.5-flash` |
| **Fallback LLM** | Groq (`openai/gpt-oss-120b` → `qwen/qwen3.8-27b`) |
| **Groq SDK** | `groq` (pip installed) |

### `.env` Keys (in `E:\flexi project\.env`)
```
GEMINI_API_KEY=...   # Active — Primary LLM
GROQ_API_KEY=...     # Active — Automatic fallback when Gemini fails
TAVILY_API_KEY=...   # Optional — mock search is built-in
N8N_WEBHOOK_URL=...  # Optional — local JSON log used when not set
```

### Installed Dependencies
`scikit-learn`, `pandas`, `numpy`, `matplotlib`, `seaborn`, `joblib`,
`python-dotenv`, `requests`, `google-genai`, `gradio`, `groq`

---

## 3. Dual-LLM Fallback Architecture

Every agent now follows this automatic chain — **zero user intervention required**:

```
Gemini (gemini-2.5-flash)
    ↓ any failure (quota / rate limit / downtime / network)
Groq → openai/gpt-oss-120b
    ↓ fails
Groq → qwen/qwen3.8-27b
    ↓ fails
Static safe-mode response (no app crash)
```

### Fallback Module
**`app/llm_fallback.py`** — Central Groq wrapper used by all agents:
```python
from app.llm_fallback import call_groq_chat
result = call_groq_chat(prompt="...", system_prompt="...", max_tokens=1200)
```

### Coverage — Agents with Groq Fallback
| File | Fallback Trigger | Fallback Action |
|---|---|---|
| `triage_agent.py` | Gemini call fails | Groq returns same JSON classification |
| `analysis_agent.py` | Gemini agentic loop fails | Groq performs text-based root-cause analysis |
| `reporter_agent.py` | Gemini call fails | Groq generates full Markdown defect report |
| `autogen_team.py` | Gemini simulation fails | Groq produces 3-agent team discussion |
| `crewai_crew.py` | Gemini simulation fails | Groq generates EDA + ML crew analysis |

---

## 4. Directory & File Inventory

```
E:\flexi project\
├── .env                                  # GEMINI_API_KEY + GROQ_API_KEY
├── README.md                             # Full documentation
├── PROJECT_CONTEXT_HANDOVER.md           # This file
├── PROJECT_REPORT_INFO_FOR_CLAUDE.md     # Ready-to-use project dossier with 16 numbered IEEE references & prompt for Claude
├── REPORT_FORMAT_FOR_CLAUDE.md           # [NEW] Exact SIT Report format matching CA3 docx template
├── PPT_FORMAT_FOR_CLAUDE.md              # [NEW] Exact SIT Presentation format matching PBL pptx template
├── test_modules.py                       # Smoke tests: memory, ML, tools, triage



├── test_agents.py                        # Integration tests: all 4 agents via Gemini
├── test_groq_fallback.py                 # Integration tests: all 4 agents via forced Groq fallback
├── run.bat                               # Double-click to start the app
│
├── app/
│   ├── __init__.py
│   ├── main.py                           # Gradio UI — 3 clean user-facing tabs
│   ├── llm_fallback.py                   # [NEW] Groq fallback module (gpt-oss-120b / qwen3.8-27b)
│   │
│   ├── agents/
│   │   ├── triage_agent.py               # Guardrail + handoff — Gemini + Groq fallback
│   │   ├── analysis_agent.py             # Root-cause analysis — Gemini + Groq fallback
│   │   ├── reporter_agent.py             # Report generation — Gemini + Groq fallback
│   │   └── autogen_team.py               # AutoGen 3-agent discussion — Gemini + Groq fallback
│   │
│   ├── memory/
│   │   └── session_store.py              # SQLite session & defect report storage
│   │
│   ├── tools/
│   │   ├── search_tool.py                # Tavily web search with mock fallback
│   │   └── n8n_tool.py                   # n8n webhook + local JSON log fallback
│   │
│   ├── ml/
│   │   ├── defect_dataset.csv            # 114 synthetic labeled defect records
│   │   ├── severity_predictor.py         # Random Forest predictor (rule-based fallback)
│   │   ├── train_model.py                # Training script
│   │   ├── severity_model.joblib         # TRAINED: 95.7% accuracy
│   │   └── training_results.png          # Confusion matrix + feature importance plots
│   │
│   ├── workflows/
│   │   ├── langgraph_workflow.py         # LangGraph StateGraph pipeline
│   │   └── crewai_crew.py                # CrewAI crew — Gemini + Groq fallback
│   │
│   └── mcp/
│       └── mcp_server.py                 # Gradio app exposed as MCP server
│
├── notebooks/
│   ├── 01_single_agent_demo.ipynb        # Unit 1 (Valid JSON, updated to google-genai)
│   ├── 02_multiagent_pipeline.ipynb      # Unit 2 (Valid JSON)
│   ├── 03_autogen_langgraph.ipynb        # Unit 3 (Valid JSON)
│   ├── 04_crewai_ml_mcp.ipynb            # Unit 4 (Valid JSON)
│   └── 05_n8n_automation.ipynb           # Unit 5 (Valid JSON)
│
└── n8n/
    └── defect_reporting_workflow.json    # Importable n8n workflow
```

---

## 5. Verification Results

| Test | Command | Result |
|---|---|---|
| Smoke tests (memory, ML, search, n8n) | `python test_modules.py` | ✅ All pass |
| Agent integration tests via Gemini | `python test_agents.py` | ✅ All 4 agents pass |
| Groq fallback tests (Gemini forced off) | `python test_groq_fallback.py` | ✅ All 4 agents pass via Groq |
| ML model training | `python app/ml/train_model.py` | ✅ 95.7% accuracy |
| All 5 Jupyter notebooks | `python fix_notebooks.py` (deleted after use) | ✅ Valid JSON |
| Main Gradio UI | `python app/main.py` | ✅ HTTP 200 on port 7860 |

---

## 6. How to Run

### Easiest — Double-click
Open `E:\flexi project` in File Explorer → double-click **`run.bat`**  
Then open: **http://localhost:7860**

### From Terminal
```powershell
cd "E:\flexi project"
python app/main.py
```

### Re-run Verification Tests
```powershell
python test_agents.py          # Normal Gemini test
python test_groq_fallback.py   # Groq fallback test (simulates Gemini failure)
```

### Retrain ML Model
```powershell
python app/ml/train_model.py
```

### Open Notebooks (Viva / Lab Demo)
```powershell
jupyter notebook notebooks/
```

### Standalone MCP Server
```powershell
python app/mcp/mcp_server.py   # Starts on port 7861
```

---

## 7. UI Description (3 Tabs — Clean, No Academic References)

The Gradio UI at **http://localhost:7860** has 3 tabs:

1. **🐛 Report & Analyze Defect** — Submit bug description → automatic triage guardrail → root-cause diagnosis → ML severity score → structured report generated + saved.
2. **👥 Multi-Agent Bug Review** — Bug Analyst + QA Engineer + Project Manager agents collaborate and produce consensus recommendations.
3. **📋 Defect History & Records** — Persistent SQLite table of all past defect submissions.

---

## 8. Key Technical Notes

- **SDK:** All agents use `google-genai` (new SDK). The old `google.generativeai` is NOT used anywhere.
- **Model:** `gemini-2.5-flash` (confirmed active via `client.models.list()`).
- **Windows encoding:** All scripts that print non-ASCII use `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` at startup.
- **PowerShell:** Does NOT support `&&`. Use separate commands or `;`.
- **Groq models available on this account:** `openai/gpt-oss-120b`, `qwen/qwen3.8-27b`, `groq/compound`, `groq/compound-mini` (as of Sept 2026).
- **n8n:** Local JSON fallback writes to `defect_reports_log.json` in project root when `N8N_WEBHOOK_URL` is not configured.
