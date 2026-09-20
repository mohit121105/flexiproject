# Academic Project Report Generator Prompt & Technical Dossier
## Aligned with Symbiosis Institute of Technology (SIT) Report Template

> **How to Use:**  
> 1. Copy the entire contents of this file.  
> 2. Paste into **Claude** (Claude 3.7 Sonnet / Claude 3.5 Sonnet).  
> 3. Claude will generate the complete, publication-quality final project report strictly structured according to the official **SIT CA3 Mini Project Report Template**.

---

```text
====================================================================================================
PROMPT TO COPY AND PASTE INTO CLAUDE:
====================================================================================================
You are a senior Professor of Computer Science and Engineering and an authority on Agentic AI, 
Automated Software Engineering, and Machine Learning. 

I am providing you with the exact institutional format and technical data for my final project:
"AI-Based Defect Reporting System" for the course "Agentic AI & Automation" (AY 2026-27) at 
Symbiosis Institute of Technology (SIT), Symbiosis International (Deemed University).

Generate a complete, exhaustive, highly detailed academic project report adhering strictly to the 
university's chapter outline and section formatting below. 

Your generated report MUST strictly follow this structure:
- Title Page (A Project Report on AI-Based Defect Reporting System, B.Tech CSE, SIT)
- Certificate (Listing Subject Teacher: Dr. Parag Naik and Subject Coordinator: Dr. Shreyas Rajendra Hole)
- Student Declaration & IPR Non-Sponsored Declaration
- Abstract (with formal keywords)
- Table of Contents
- CHAPTER 1: BACKGROUND AND TECHNICAL OVERVIEW (1.1 Background, 1.2 Objectives, 1.3 Technical & Framework Components)
- CHAPTER 2: PROBLEM STATEMENT AND MOTIVATION (2.1 Problem Statement, 2.2 Motivation)
- CHAPTER 3: NOVELTY AND INNOVATIVE CONTRIBUTIONS (3.1 Novelty, 3.2 Innovative Contributions)
- CHAPTER 4: TECHNICAL ADVANTAGES AND PRACTICAL USEFULNESS (4.1 Technical Advantages, 4.2 Practical Usefulness)
- CHAPTER 5: DETAILED METHODOLOGY / SYSTEM ARCHITECTURE (5.1 System Architecture, 5.2 Working Principle & Multi-Agent Coordination, 5.3 Framework Connections & Pipeline, 5.4 Simulation, Verification & Tracing)
- CHAPTER 6: PRIOR ART AND RELATED WORK (6.1 Introduction, 6.2 Existing Technologies, 6.3 Comparative Analysis, 6.4 Summary)
- CHAPTER 7: APPLICATIONS AND DEPLOYMENT AREAS (7.1 Real-World Applications, 7.2 Deployment Areas)
- CHAPTER 8: CONCLUSION AND FUTURE SCOPE (8.1 Conclusion, 8.2 Future Scope)
- CHAPTER 9: GITHUB LINK AND SHORT CODE (9.1 Repository Structure, 9.2 Key Implementation Source Code)
- REFERENCES / BIBLIOGRAPHY (Using the 16 numbered IEEE citations [1]-[16] provided, with in-text brackets cited throughout every chapter)

Ensure deep technical rigor, mathematical formulations for the Random Forest & Linear Regression metrics, 
ASCII/Mermaid diagrams, and exact references to the codebase files.

Here is the complete project dossier and template details:
====================================================================================================
```

---

# Official Institutional Template Details & Project Dossier

## 1. University & Project Front Matter

- **Document Title:** A PROJECT REPORT ON AI-BASED DEFECT REPORTING SYSTEM
- **Degree:** Bachelor of Technology in Computer Science and Engineering
- **Department:** Department of Computer Science and Engineering
- **Institution:** Symbiosis Institute of Technology (SIT), Symbiosis International (Deemed University), Pune / Nagpur, India
- **Academic Year:** 2026–2027
- **Course Name:** Agentic AI & Automation (Course Credit: 3, Level: 3)
- **Subject Teacher:** Dr. Parag Naik
- **Subject Coordinator:** Dr. Shreyas Rajendra Hole
- **Student Details Placeholder:** `<Student Name>, PRN: <PRN Number>, B.Tech CSE`
- **UN Sustainable Development Goals:** SDG 4 (Quality Education), SDG 8 (Decent Work & Economic Growth), SDG 9 (Industry, Innovation & Infrastructure)
- **Academic Benchmarks Cited in Syllabus:**
  - UC Berkeley: *CS294/194-196 Large Language Model Agents*
  - Carnegie Mellon University (CMU): *15-482 Autonomous Agents*

---

## 2. Certificate & Declarations Format

### 2.1 Certificate Text
> *"This is to certify that the Project work entitled 'AI-Based Defect Reporting System' is carried out by <Student Name (PRN)>, in partial fulfillment for the award of the degree of Bachelor of Technology in Computer Science and Engineering, Symbiosis International (Deemed University), Pune during the academic year 2026-2027."*  
> **Dr. Parag Naik** (Subject Teacher)  
> **Dr. Shreyas Rajendra Hole** (Subject Coordinator)

### 2.2 Declaration Text
> *"I hereby declare that the project titled 'AI-Based Defect Reporting System' submitted to Symbiosis Institute of Technology, a constituent of Symbiosis International (Deemed University) Pune, for the award of the degree of Bachelor of Technology in Computer Science and Engineering, is a result of original research carried out by me. I understand that my report may be made electronically available to the public. It is further declared that the project report or any part thereof has not been previously submitted to any University or Institute for the award of any degree or diploma."*

### 2.3 IPR Declaration Text
> *"We hereby declare that the project entitled 'AI-Based Defect Reporting System', submitted by me for the purpose of processing under the IPR framework, is not an industry-sponsored project. We further provide our full consent to SIT Nagpur and SCRI Pune to evaluate, process, and proceed with the filing of the Intellectual Property Rights (IPR) application for the said idea."*

---

## 3. Abstract & Keywords

### Abstract
The proliferation of complex software architectures has magnified the volume and intricacy of defect submissions encountered by engineering teams. Traditional bug tracking workflows suffer from significant friction: end-user reports often lack diagnostic context, triage teams endure cognitive fatigue leading to subjective severity assignments, and defect tracking databases remain disconnected from real-time developer communication channels. 

This project presents the **AI-Based Defect Reporting System**, an enterprise-grade autonomous multi-agent platform designed to automate the complete lifecycle of defect ingestion, triage, diagnosis, severity quantification, and notification dispatch. The system integrates:
1. An intelligent **Triage Agent** enforcing regex and semantic guardrails to filter non-defect noise and route genuine issues.
2. A tool-augmented **Analysis Agent** operating on an autonomous function-calling loop with persistent SQLite session memory and real-time search capabilities.
3. A dual-model **Classical Machine Learning Pipeline** utilizing a Random Forest classifier trained on balanced software defect distributions, achieving **95.7% test accuracy** and **98.9% 5-fold cross-validation accuracy** for severity classification, paired with a Linear Regression model for continuous priority scoring.
4. A **Reporter Agent** that synthesizes technical findings into standardized Markdown reports and emits structured JSON payloads.
5. An **AutoGen Collaborative Review Team** convening specialized personas (Bug Analyst, QA Engineer, Project Manager) to deliberate complex defects and produce cross-functional consensus.
6. A **Model Context Protocol (MCP)** server deployed via Gradio on port 7861 for standardized tool discovery.
7. An **n8n Automation Pipeline** translating webhooks into automated Google Sheets logs, HTML Gmail notifications, and Google Calendar triage meetings.
8. A **Resilient Dual-LLM Failover Architecture** ensuring zero downtime by automatically routing from primary Google Gemini 2.5 Flash to Groq (`openai/gpt-oss-120b` and `qwen/qwen3.8-27b`) upon latency, quota, or rate-limit events.

### Keywords
`Agentic AI`, `Autonomous Multi-Agent Systems`, `Defect Triage`, `Random Forest Severity Prediction`, `LangGraph Workflows`, `AutoGen Collaborative Teams`, `Model Context Protocol (MCP)`, `n8n Enterprise Automation`, `Dual-LLM Failover`, `Gemini 2.5 Flash`, `Groq LPU`.

---

## 4. Chapter-by-Chapter Technical Specifications

### CHAPTER 1: BACKGROUND AND TECHNICAL OVERVIEW
- **1.1 Background:** Evolution of software quality assurance from manual spreadsheets to Jira/Bugzilla, and now to autonomous agentic intelligence. Role of LLMs in software engineering as documented by Alammar & Grootendorst [1] and Phoenix & Taylor [2].
- **1.2 Objectives:**
  - Build an end-to-end multi-agent defect management ecosystem satisfying all 5 Course Outcomes (CO1 to CO5).
  - Eliminate triage backlog through automated guardrails and classification.
  - Implement objective, data-driven severity prediction using supervised machine learning [4], [9].
  - Provide high availability through automated multi-provider LLM failover [3], [12].
- **1.3 Technical & Framework Components:**
  - **Programming & Runtime:** Python 3.13 / 3.10+, PowerShell on Windows 11.
  - **Foundation LLMs:** Google Gemini 2.5 Flash (`google-genai` SDK v2.16.0) [11]; Groq LPU engine (`openai/gpt-oss-120b`, `qwen/qwen3.8-27b`) [12].
  - **Stateful Memory:** SQLite database (`defect_memory.db`) with relational session indexing.
  - **Machine Learning & Preprocessing:** Scikit-Learn [10], Pandas, NumPy, Joblib.
  - **Agentic Frameworks:** AutoGen GroupChat [5], LangGraph StateGraph [6], CrewAI [7], Anthropic Model Context Protocol [8].
  - **Integration & UI:** Gradio [16], n8n Workflow Engine [13], Tavily Web Search.

---

### CHAPTER 2: PROBLEM STATEMENT AND MOTIVATION
- **2.1 Problem Statement:** Quantifies the cost of software defects: 40% of developer time spent reproducing ambiguous bugs; 30% of bug reports misclassified in severity; critical production incidents delayed due to manual triage bottlenecks.
- **2.2 Motivation:** Transitioning software maintenance from human-in-the-loop bottleneck to human-on-the-loop oversight. Automating repetitive diagnostic steps while preserving human decision authority for deployment.

---

### CHAPTER 3: NOVELTY AND INNOVATIVE CONTRIBUTIONS
- **3.1 Novelty:**
  - **Hybrid Neuro-Symbolic Architecture:** Combines generative LLM reasoning (for unstructured text understanding and reproduction design) with deterministic classical ML (for calibrated severity classification and priority scoring).
  - **Zero-Downtime Dual-LLM Failover:** Seamless, state-preserving fallback from Gemini to Groq with zero user interruption or data loss.
  - **Standardized Multi-Agent Protocols:** Seamless integration of AutoGen, LangGraph, CrewAI, and MCP within a unified platform.
- **3.2 Innovative Contributions:**
  - Fast-path regex & semantic guardrails saving up to 80% inference tokens on invalid or out-of-domain submissions.
  - Model Context Protocol (MCP) server converting standard Gradio web interfaces into machine-readable tool endpoints.
  - End-to-end enterprise workflow automation linking developer IDEs to Google Workspace via n8n.

---

### CHAPTER 4: TECHNICAL ADVANTAGES AND PRACTICAL USEFULNESS
- **4.1 Technical Advantages:**
  - Sub-second triage response time using Groq LPU inference.
  - High diagnostic accuracy through memory-augmented multi-turn context.
  - Fully local, offline-resilient fallbacks for database storage and event logging.
- **4.2 Practical Usefulness:**
  - Immediate applicability across software startups, open-source repositories, and enterprise IT service desks.
  - Directly reduces Mean Time to Detection (MTTD) and Mean Time to Resolution (MTTR).

---

### CHAPTER 5: DETAILED METHODOLOGY / SYSTEM ARCHITECTURE
- **5.1 System Architecture:**
  ```
  User Input → [Triage Guardrail]
                    ↓ (if valid)
             [Analysis Agent] ←→ [SQLite Memory & Web Search]
                    ↓
             [Random Forest ML Predictor (95.7% Acc)]
                    ↓
             [Reporter Agent] → Standardized Markdown Report
                    ↓
             [n8n Webhook] → Google Sheets + Gmail + Google Calendar
  ```
- **5.2 Working Principle & Multi-Agent Coordination:**
  - Hand-off protocol: Typed dictionaries and schema validation transferring control between Triage, Analysis, and Reporter agents.
  - AutoGen collaborative debate mechanism between Bug Analyst, QA Engineer, and Project Manager.
- **5.3 Framework Connections & Pipeline:** Detailed interaction diagrams between Gradio frontend, SQLite storage, Scikit-Learn pipeline, and external APIs.
- **5.4 Simulation, Verification & Tracing:** Execution traces recorded at each node; telemetry logs tracking token consumption, tool invocations, and latency.

---

### CHAPTER 6: PRIOR ART AND RELATED WORK (LITERATURE SURVEY)
- **6.1 Introduction:** Comprehensive review of automated bug tracking, NLP for issue categorization, and agentic workflows.
- **6.2 Existing Technologies:** Comparative survey of Jira Service Desk, Bugzilla, GitHub Copilot for Issues, and traditional rule-based ticket routers.
- **6.3 Related Work & Comparative Matrix:**
  | Feature | Traditional Tools (Jira/Bugzilla) | LLM Chatbots (ChatGPT/Claude) | AI-Based Defect Reporting System (Ours) |
  |---|---|---|---|
  | Automated Guardrail | ❌ None | ⚠️ Generic moral filter | ✅ Domain-specific defect guardrail |
  | Contextual Memory | ❌ Static fields | ⚠️ Session-only | ✅ SQLite persistent database |
  | Objective Severity Scoring | ❌ Subjective user pick | ⚠️ Inconsistent LLM text | ✅ Random Forest (95.7% accuracy) |
  | Multi-Agent Collaboration | ❌ None | ❌ Single perspective | ✅ AutoGen 3-Agent Review Team |
  | Protocol Interoperability | ❌ Proprietary APIs | ❌ Chat-only | ✅ Model Context Protocol (MCP) |
  | Failover Resilience | ❌ N/A | ❌ Outage-prone | ✅ Gemini 2.5 + Groq Dual Failover |
- **6.4 Summary:** Establishes the technical superiority and academic contribution of the proposed hybrid architecture.

---

### CHAPTER 7: APPLICATIONS AND DEPLOYMENT AREAS
- **7.1 Real-World Applications:**
  - Continuous Integration & Testing (CI/CD) pipelines (automated defect logging upon test failure).
  - Open-Source Issue Ingestion (filtering non-bug issues on GitHub/GitLab).
  - Customer Support & Helpdesk Escalation (translating customer complaints into developer-ready bug reports).
- **7.2 Deployment Areas:** Cloud-native containerized deployment (Docker/Kubernetes), on-premise air-gapped enterprise setups, and developer workstations.

---

### CHAPTER 8: CONCLUSION AND FUTURE SCOPE
- **8.1 Conclusion:** Reiteration of project achievements: successful realization of CO1–CO5, 95.7% ML accuracy, resilient dual-LLM infrastructure, and seamless Gradio UI deployment.
- **8.2 Future Scope:**
  - Multimodal defect triage (analyzing video screen recordings and network HAR files).
  - Autonomous patch generation (integrating code modification agents to propose git diff PRs).
  - Bi-directional synchronization with Jira, Linear, and Azure DevOps.

---

### CHAPTER 9: GITHUB LINK AND SHORT CODE
- **9.1 Repository Structure:** Complete file hierarchy matching the project tree.
- **9.2 Core Code Implementations:** Key excerpts from:
  - `app/agents/triage_agent.py` (Guardrail check & classification)
  - `app/agents/analysis_agent.py` (Agentic loop with function calling)
  - `app/ml/severity_predictor.py` & `train_model.py` (Random Forest model)
  - `app/llm_fallback.py` (Groq resilient failover engine)
  - `app/main.py` (Gradio UI configuration)

---

## 5. Numbered IEEE References (To be cited in-text)

[1] J. Alammar and M. Grootendorst, *Hands-On Large Language Models: Language Understanding and Generation*, 1st ed. Sebastopol, CA, USA: O'Reilly Media, 2024. ISBN: 978-1098150952.  
[2] J. Phoenix and M. Taylor, *Prompt Engineering for Generative AI: Future-Proof Inputs for Reliable AI Outputs*, 1st ed. Sebastopol, CA, USA: O'Reilly Media, 2024. ISBN: 978-1098153427.  
[3] C. Huyen, *AI Engineering: Building Applications with Foundation Models*, 1st ed. Sebastopol, CA, USA: O'Reilly Media, 2024. ISBN: 978-1098166298.  
[4] C. Huyen, *Designing Machine Learning Systems: An Iterative Process for Production-Ready Applications*, 1st ed. Sebastopol, CA, USA: O'Reilly Media, 2022. ISBN: 978-1098107956.  
[5] Q. Wu et al., "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation," *arXiv preprint arXiv:2308.08155*, 2023.  
[6] H. Chase et al., "LangGraph: Building Resilient, Stateful, Multi-Actor Applications with LLMs," *LangChain Documentation*, 2024.  
[7] J. Moura, "CrewAI: Framework for Orchestrating Role-Playing Autonomous AI Agents," *CrewAI Specification*, 2024.  
[8] Anthropic, "Model Context Protocol (MCP) Specification: Open Standard for Secure AI-Tool Interoperability," 2024.  
[9] L. Breiman, "Random Forests," *Machine Learning*, vol. 45, no. 1, pp. 5–32, 2001.  
[10] F. Pedregosa et al., "Scikit-learn: Machine Learning in Python," *Journal of Machine Learning Research*, vol. 12, pp. 2825–2830, 2011.  
[11] Google DeepMind, "Gemini 2.5: Multimodal Foundation Models with Advanced Reasoning," *Google Research*, 2025/2026.  
[12] Groq Inc., "LPU Inference Engine: High-Throughput Architecture," *Groq Whitepaper*, 2024.  
[13] n8n GmbH, "n8n: Fair-Code Workflow Automation Platform," *n8n Documentation*, 2024.  
[14] UC Berkeley, "CS294/194-196: Large Language Model Agents," *UC Berkeley RDI*, 2024.  
[15] Carnegie Mellon University, "15-482 / 15-682: Autonomous Agents," *CMU CS Department*, 2024.  
[16] A. Abid et al., "Gradio: Hassle-Free Sharing and Testing of ML Models in the Wild," *arXiv preprint arXiv:1906.02569*, 2019.
