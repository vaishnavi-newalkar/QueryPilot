# 🚀 QueryPilot

### Agent‑Based Self‑Serve Analytics for Large Datasets

QueryPilot is an **agent‑driven analytics platform** that allows users to explore CSV and Excel datasets using **natural language**, without writing SQL.

It is designed as a **realistic analytics MVP** for startups and internal teams, focusing on **correctness, scalability, and user safety** rather than UI gimmicks.

QueryPilot safely converts natural‑language questions into optimized SQL queries, executes them using DuckDB, and provides clear insights — even on **large datasets**.

---

## ✨ Why QueryPilot?

Most data tools fail in one of two ways:

* They require SQL expertise, or
* They allow unsafe queries that break on large data

**QueryPilot solves both.**

It acts as a *pilot* for your data — guiding users toward efficient, meaningful analysis while preventing costly mistakes.

---

## 🧠 Key Capabilities

### 💬 Conversational Analytics (Default Mode)

* Ask questions in plain English
* Automatic **NLP → SQL translation** using an agent‑based architecture
* All computations executed via **DuckDB** (LLM never calculates data)
* Built‑in safety rules for large datasets
* No SQL knowledge required

---

### 📊 Full Dataset Analysis (Opt‑In)

* Explicitly triggered by the user (never runs automatically)
* Generates a structured **Exploratory Data Analysis (EDA)** report
* Includes:

  * Dataset overview (rows, columns, size)
  * Schema and data types
  * Missing value analysis
  * Descriptive statistics
  * Distributions and correlation heatmaps
  * Data quality summary
* Uses sampling and aggregation for performance on large datasets

---

### 🛡️ Large Dataset Safety by Design

* Automatic dataset size detection
* Lightweight preprocessing for large files
* Heavy computation delegated to DuckDB
* Result‑size limits and aggregation‑first querying
* Progressive disclosure: summaries by default, depth on demand

---

### 🤖 Agent‑Based Intelligence

* LLM used **only for reasoning and query generation**
* Deterministic tools (DuckDB, Pandas) handle execution
* Ambiguous questions trigger clarification, not guesses
* Session‑aware conversational context using SQLite persistence

---

## 🧩 System Architecture

### High‑Level Architecture

```
                ┌────────────────────┐
                │        User         │
                │ (Natural Language)  │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │    Streamlit UI     │
                │  (Modes + Controls) │
                └─────────┬──────────┘
                          │
          ┌───────────────┴────────────────┐
          │                                 │
          ▼                                 ▼
┌────────────────────┐         ┌────────────────────┐
│ Conversational Mode│         │ Full Dataset Analysis│
│  (Safe Queries)    │         │  (EDA + Visuals)    │
└─────────┬──────────┘         └─────────┬──────────┘
          │                                 │
          ▼                                 ▼
┌─────────────────────────────────────────────────────┐
│                 QueryPilot Agent (Agno)              │
│  - Interprets user intent                            │
│  - Translates NL → SQL                               │
│  - Enforces safety & ambiguity rules                 │
│  - Maintains session memory                          │
└─────────┬───────────────────────────────────────────┘
          │
          ▼
┌────────────────────┐
│     DuckDB Engine  │
│  (SQL Execution)   │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Results & Insights │
│ (Summaries / Plots)│
└────────────────────┘
```

---

## 🏗️ Design Principles

### 1. Separation of Responsibilities

* **LLM** → intent understanding & SQL generation
* **DuckDB** → all computation and aggregation
* **Pandas** → lightweight preprocessing & previews only

### 2. Safety Over Convenience

* No unbounded `SELECT *` on large datasets
* Automatic limits and aggregation‑first queries
* Ambiguous terms trigger clarification

### 3. Progressive Disclosure

* Fast answers by default
* Heavy analysis only when explicitly requested
* Prevents accidental expensive operations

### 4. Scalable by Design

* Suitable for MVP and internal tools
* Clear migration path to data warehouses
* Model‑agnostic LLM layer (OpenAI‑compatible APIs)

---

## 🛠️ Tech Stack

* **Python**
* **Streamlit** – UI & interaction layer
* **Agno** – Agent orchestration & tool calling
* **DuckDB** – Analytical SQL execution engine
* **Pandas / NumPy** – Preprocessing & summaries
* **Plotly / Matplotlib / Seaborn** – Visualizations
* **SQLite** – Session & conversation persistence
* **Groq‑hosted LLM** (OpenAI‑compatible API)

---

## 📂 Project Structure

```
├── app.py                  # Main Streamlit application
├── eda_helpers.py          # Full dataset analysis utilities
├── agent_sessions.db       # SQLite DB for session persistence
├── .env                    # Environment variables
├── requirements.txt
└── README.md
```

---

## ⚙️ How QueryPilot Works

1. User uploads a CSV or Excel file
2. Dataset size is detected and classified (small / large)
3. Data is lightly preprocessed and loaded into DuckDB
4. User selects:

   * Conversational Analytics **or**
   * Full Dataset Analysis
5. QueryPilot Agent:

   * Interprets intent
   * Generates optimized SQL
   * Enforces safety & performance rules
6. DuckDB executes the query
7. Results and insights are displayed to the user

---

## 🔮 Future Enhancements

* Query advisory / optimization suggestions
* Context‑aware question recommendations
* Cached analysis reports
* Role‑based access & authentication
* Warehouse‑backed execution (BigQuery / Snowflake)

---

## 🎯 Why This Project Matters

QueryPilot demonstrates:

* Agent‑based system design
* Practical NLP → SQL translation
* Large dataset handling
* Product‑oriented UX decisions
* Startup‑ready engineering trade‑offs

This is **not a toy demo** — it is a realistic analytics MVP built with production thinking.

---

## 🧑‍💻 Author

Built with a focus on **clarity, safety, and scalability**, prioritizing real‑world data workflows over superficial polish.

---

### ✅ Final Note

QueryPilot is intentionally designed to be:

* Easy to use for non‑technical users
* Safe for large datasets
* Easy to extend and productionize

Perfect for startup demos, internal tools, and technical interviews.
