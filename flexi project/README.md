# 🤖 AI-Based Defect Reporting System

> **Course:** Agentic AI & Automation — Symbiosis International University  
> **Project Type:** Capstone / Mini-Project  
> **Coverage:** All 5 course units (CO1–CO5)

---

## 📌 Project Overview

An end-to-end **AI-powered defect reporting and analysis system** that uses multiple agentic AI frameworks to:
- Accept defect reports from users via a Gradio web UI
- Triage, analyze, and classify defects using AI agents with persistent memory
- Predict defect severity using a classical ML model (Random Forest)
- Generate structured reports using a CrewAI multi-agent crew
- Automate stakeholder notifications via n8n (Gmail + Google Sheets + Calendar)

---

## 🗂️ Project Structure

```
flexi project/
├── .env                          # API keys (Gemini, Tavily, n8n)
├── .env.example                  # Template for .env
├── requirements.txt              # All dependencies
├── README.md                     # This file
│
├── app/
│   ├── main.py                   # 🎯 Gradio UI entry point (run this!)
│   ├── agents/
│   │   ├── triage_agent.py       # Unit 2: Guardrail + handoff
│   │   ├── analysis_agent.py     # Unit 1: Gemini agent + SQLite memory + tools
│   │   ├── reporter_agent.py     # Unit 2: Report generation agent
│   │   └── autogen_team.py       # Unit 3: AutoGen multi-model team
│   ├── workflows/
│   │   ├── langgraph_workflow.py # Unit 3: LangGraph stateful workflow
│   │   └── crewai_crew.py        # Unit 4: CrewAI defect analysis crew
│   ├── ml/
│   │   ├── defect_dataset.csv    # Synthetic defect training data
│   │   ├── severity_predictor.py # Unit 4: Random Forest severity model
│   │   └── train_model.py        # Training + evaluation script
│   ├── mcp/
│   │   └── mcp_server.py         # Unit 4: Gradio-based MCP server
│   ├── memory/
│   │   └── session_store.py      # Unit 1: SQLite session memory
│   └── tools/
│       ├── search_tool.py        # Unit 1: Web search FunctionTool
│       └── n8n_tool.py           # Unit 5: n8n webhook tool
│
├── notebooks/
│   ├── 01_single_agent_demo.ipynb
│   ├── 02_multiagent_pipeline.ipynb
│   ├── 03_autogen_langgraph.ipynb
│   ├── 04_crewai_ml_mcp.ipynb
│   └── 05_n8n_automation.ipynb
│
└── n8n/
    └── defect_reporting_workflow.json   # Import into n8n
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Your .env file already exists with GEMINI_API_KEY
# Optionally add TAVILY_API_KEY and N8N_WEBHOOK_URL
```

### 3. Train the ML Model
```bash
python app/ml/train_model.py
```

### 4. Launch the App
```bash
python app/main.py
```
Open your browser at `http://localhost:7860`

---

## 🧠 How It Works (Agent Flow)

```
User submits defect report
        ↓
[Triage Agent] — checks if it's a valid defect (guardrail)
        ↓ handoff
[Analysis Agent] — Gemini LLM with SQLite memory + web search
        ↓ tool call
[ML Severity Predictor] — Random Forest → Low/Medium/High/Critical
        ↓
[CrewAI Crew] — Bug Analyst + QA Engineer + PM discuss the defect
        ↓
[Reporter Agent] — generates structured Markdown + JSON report
        ↓
[n8n Webhook] — logs to Google Sheets, emails team, creates Calendar event
```

---

## 📚 Course Units Covered

| Unit | Topic | Files |
|------|-------|-------|
| 1 | OpenAI/Gemini Agents SDK, SQLite memory, Tavily search | `analysis_agent.py`, `session_store.py`, `search_tool.py` |
| 2 | Multi-agent, guardrails, handoffs | `triage_agent.py`, `reporter_agent.py` |
| 3 | AutoGen multi-model + LangGraph + Gradio | `autogen_team.py`, `langgraph_workflow.py` |
| 4 | CrewAI + sklearn ML + MCP server | `crewai_crew.py`, `severity_predictor.py`, `mcp_server.py` |
| 5 | n8n automation + Gmail + Sheets + Calendar | `n8n_tool.py`, `defect_reporting_workflow.json` |

---

## 🔑 API Keys Needed

| Key | Required? | Where to Get |
|-----|-----------|--------------|
| `GEMINI_API_KEY` | ✅ Yes | [Google AI Studio](https://aistudio.google.com/) |
| `TAVILY_API_KEY` | ⚡ Optional | [tavily.com](https://tavily.com) (free tier) |
| `N8N_WEBHOOK_URL` | ⚡ Optional | After importing `n8n/defect_reporting_workflow.json` |
| `OPENAI_API_KEY` | ⚡ Optional | For AutoGen GPT-4o agent (Gemini used as fallback) |

---

## 📓 Notebooks

Each notebook is a standalone demo for its unit — ideal for viva/presentation:

1. `01_single_agent_demo.ipynb` — Single Gemini agent with memory and tools
2. `02_multiagent_pipeline.ipynb` — Triage → Analysis → Reporter chain
3. `03_autogen_langgraph.ipynb` — AutoGen team + LangGraph visualization
4. `04_crewai_ml_mcp.ipynb` — CrewAI crew + ML model + MCP
5. `05_n8n_automation.ipynb` — n8n workflow integration

---

## 🛠️ Technologies Used

`Google Gemini` · `LangGraph` · `AutoGen` · `CrewAI` · `Gradio` · `scikit-learn` · `SQLite` · `n8n` · `Tavily` · `Python 3.10+`
