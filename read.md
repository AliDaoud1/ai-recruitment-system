# 🧠 AI Recruitment System (CV Analyser + Hiring Agent)

An AI-powered recruitment platform that combines **CV analysis** and **candidate hiring evaluation** using:

- 🔍 RAG (Retrieval-Augmented Generation)
- 🧠 Vector memory (semantic memory for conversations)
- 🔐 PII detection & sanitization
- 📊 LLM-based scoring system
- 🧾 Audit logging (structured system tracking)
- ⚙️ Dual-system architecture (CV Analyser + Hiring Agent)

This system helps recruiters:
- Analyze and understand CVs deeply
- Extract skills and improve sections
- Score candidates against job descriptions
- Compare multiple candidates fairly
- Select and recommend top talent

---

# 🚀 Features

## 📄 1. CV Ingestion (RAG Pipeline)

- Supports `.pdf` and `.txt` CVs
- Automatic chunking for optimal retrieval
- Embedding storage in vector DB (Pinecone)
- Namespace-based storage (Hiring mode)

---

## 🔎 2. CV Intelligence (Analyser System)

- Select and inspect individual CVs
- Generate:
  - Summary
  - Skills extraction
  - Section improvement
- Semantic search across CV database
- Supports MMR (diversity search toggle)

---

## 🧠 3. Memory System

- Stores conversation history
- Enables:
  - Follow-up questions
  - Context-aware answers
  - Cross-session recall

---

## 🔐 4. Security Layer (PII Redaction)

Automatically removes:

- Emails → `[EMAIL]`
- Phone numbers → `[PHONE]`
- LinkedIn / GitHub links → `[LINK]`

Applied BEFORE:
- indexing
- LLM input
- memory storage

---

## 📊 5. Hiring System (Candidate Scoring Engine)

### Features:
- Score candidates against job description
- Structured evaluation:
  - Technical score (1–10)
  - Experience score (1–10)
  - Nice-to-have score (1–10)
  - Total score
- LLM-generated reasoning
- Candidate comparison (ranked table)
- Final recommendation output

---

## 🧾 6. Audit System (Unified Logging)

Tracks system behavior:

### Events logged:
- Candidate selection
- Job description loading
- Candidate scoring
- Candidate comparison
- Recommendations
- System exit
- MMR toggles


# 🏗️ System Architecture

```text
User Input
    ↓
Command Handler
    ↓
Agent Layer (Analyser / Hiring)
    ↓
Vector Retrieval (RAG)
    ↓
Memory Layer (optional context)
    ↓
LLM (Gemini)
    ↓
Structured Output
    ↓
Audit Logging + Memory Update
```

---

# 📂 Project Structure

```text
project/
│
├── agents/
│   ├── cv_analyser_agent.py
│   └── hiring_agent.py
│
├── services/
│   ├── llm_client.py
│   ├── embedding_service.py
│   ├── document_store.py
│   ├── vector_memory_store.py
│   ├── cv_security_parser.py
│   ├── audit_logger.py
│   ├── logger.py
│   ├── file_helper.py
│   └── cv_prompts.py
│
├── app/
│   ├── command_handler.py
│   ├── hiring_command_handler.py
│   ├── file_loader.py
│   ├── session_manager.py
│   └── app_container.py
│
├── data/
│   ├── candidate CVs
│   └── job_description
│
├── logs/
│   ├── analyser_app.log
│   ├── hiring_app.log
│   └── audit_log.json
│
└── main_analyser.py
└── main_hiring.py
```

---

# ⚙️ Installation

## 1. Clone project

```bash
git clone <your_repo_url>
cd cv-analyser-agent
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Environment Variables

Create `.env`:

```env
GEMINI_API_KEY=your_key
GEMINI_MODEL_NAME=gemini-1.5-flash
GEMINI_TEMPERATURE=0.0
GEMINI_EMBEDDING_MODEL=models/text-embedding-004

PINECONE_API_KEY=your_key
PINECONE_INDEX_NAME=your_index
PINECONE_NAMESPACE=cv_analyser
```

---

# ▶️ Running

```bash
# CV Analyser
python main_analyser.py

# Hiring System
python main_hiring.py
```

---

# 🔒 Security Example

### Before sanitization:

```text
ali@example.com
+972-555-5555
linkedin.com/in/example
```

### After sanitization:

```text
[EMAIL]
[PHONE]
[LINKEDIN]
```

---

# 🧠 Key Design Principles
* Separation of concerns (Analyser vs Hiring)
* RAG-first architecture
* Structured LLM outputs (JSON enforced)
* Auditability of all actions
* Memory-enhanced conversation system
* Namespace isolation per candidate

# 📈 Future Improvements

* Web UI dashboard (React / FastAPI)
* Multi-agent collaboration (Reviewer / Recruiter / Ranker)
* Automatic CV parsing into structured schema
* Bias detection in scoring
* Job-to-candidate matching engine
* Real-time candidate ranking updates

# ⚡ Performance & Cost Optimization
* score_all currently makes one LLM call per candidate → high cost and latency
* Full CV + job description sent each time → high token usage
* Planned batch scoring to reduce number of LLM calls
* Two-stage pipeline: fast pre-filter → LLM only for top candidates
* CV context compression (extract only key skills/experience)
* Caching results per job description to avoid re-scoring
* Prompt optimization to reduce unnecessary tokens while keeping structured output

---

# 🛠️ Tech Stack

* Python
* LangChain
* Google Gemini
* Pinecone
* Vector Embeddings
* RAG architecture
* JSON-based audit system

---

# 📁 Sample Inputs

The system includes sample input data used for testing both the CV Analyser and Hiring Agent.

## 📄 Job Descriptions

The `job_description/` folder contains example job requirements used by the Hiring Agent for candidate scoring and comparison.

These files simulate real-world job postings and help evaluate:
- Technical fit
- Experience level
- Required skills
- Startup / role alignment

## 📄 CV Data

The `data/` folder contains sample CVs used by the CV Analyser system for retrieval, summarization, and skill extraction.

> ⚠️ Note: All data is synthetic or anonymized and used only for demonstration purposes.
# 📌 Example Recruiter Query

```text
ask Which candidate is best for a backend AI startup under $12k/month?
```

System evaluates:

* Backend expertise
* AI knowledge
* Startup fit
* Communication indicators
* Technical breadth

---

# 👨‍💻 Author

* Built as an AI-powered recruitment intelligence system for CV analysis, hiring automation, and candidate evaluation.
---

