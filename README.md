# 🏦 Bank Reconciliation System – Core Logic Engine

A scalable, modular **transaction reconciliation backend** designed for fintech / accounting / ERP use-cases.

This system performs automated reconciliation between **bank statements and accounting system exports (e.g., Yardi)** using a hybrid architecture:

- Deterministic Matching Engines
- Heuristic Similarity Matching
- AI Assisted Reconciliation (RAG based)
- Learning Feedback Loop (future capability)

---

## 🚀 Key Features

### ✅ Universal File Ingestion

Supports multiple input formats:

- CSV
- XLSX / XLS
- TXT
- BAI files
- PDF statements (basic parsing)

Automatic schema detection and normalization:

- Date standardization
- Amount cleaning & sign normalization
- Reference token normalization
- Description canonicalization

---

### ✅ Multi-Layer Matching Engine

#### 1. Exact Matching

Fast deterministic reconciliation based on:

- amount
- normalized reference
- transaction date

Used for high-confidence matches.

---

#### 2. Hash Matching Engine

Uses hashed composite keys for efficient large dataset matching.

Benefits:

- O(N) lookup performance
- Suitable for high-volume reconciliation batches
- Memory efficient indexing

---

#### 3. Heuristic Matching Engine

Handles real-world reconciliation challenges:

- Date tolerance window
- Amount tolerance
- Description token similarity
- Reference fuzziness

Improves match coverage beyond exact logic.

---

### ✅ Candidate Index Engine

Creates searchable indices of transactions:

- amount buckets
- reference clusters
- description token inverted index

Used to reduce AI search space.

---

### 🤖 AI Assisted Reconciliation (RAG)

AI layer is used **only for unresolved mismatches**.

Capabilities:

- Suggest possible match candidates
- Explain mismatch reasons
- Learn from historical reconciliation patterns
- Vector similarity search over previous corrections

Architecture uses:

- Vector DB (FAISS / Chroma)
- Embeddings (HuggingFace / OpenAI)
- Retrieval-Augmented Generation

---

### 📈 Matching Evaluation Mode

Offline benchmarking tool to measure:

- Exact match %
- Hash match %
- Heuristic match %
- Total reconciliation coverage

Used to tune thresholds and improve engine quality.

---

### 📂 File Upload Manager

Supports uploading reconciliation documents from local system.

Workflow:


Local File → Validation → Stored in data/uploads → Normalized → Ready for Matching


Ensures:

- Unique filenames
- Auditability
- Safe ingestion pipeline

---

### 🧠 Future Learning Loop

Planned capability:

- User approves / rejects AI suggestions
- System stores feedback
- Matching confidence improves over time
- Adaptive reconciliation intelligence

---

## 🏗️ Project Architecture


app/

ingestion/
loader.py
file_manager.py
bai_parser.py

normalization/
normalize.py

matching/
exact_match.py
hash_match.py
heuristic_hash_match.py
candidate_engine.py

ai_services/
rag_service.py
ai_match_suggester.py

learning/
ai_learning_loop.py

pipeline/
reconciliation_orchestrator.py

utils/
logger.py

tests/
test_matching.py
matching_evaluation.py

data/
uploads/


---

## ⚙️ Installation

```bash
git clone <repo-url>
cd Bank-Reconcilation-System-Core-logic

python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate

pip install -r requirements.txt
▶️ Run Reconciliation
python main.py
📊 Run Matching Evaluation
python -m tests.matching_evaluation

Outputs:

Total transactions
Match coverage %
Engine contribution breakdown
🤖 AI Mode (Optional)

Set environment variable:

OPENAI_API_KEY=your_key

Then system will enable AI suggestion layer.

🎯 Use Cases
Bank vs Ledger reconciliation
Property management accounting reconciliation
ERP transaction validation
Payment gateway settlement matching
Financial audit assistance
High volume fintech reconciliation automation
⚠️ Current Limitations
BAI parsing is simplified
PDF parsing requires structured statements
AI suggestion confidence calibration in progress
No distributed processing yet
UI / API layer not included
🛣️ Roadmap
Confidence scoring engine
Merchant semantic clustering
Feedback driven rule learning
FastAPI reconciliation service
Batch job scheduler
Reconciliation analytics dashboard
Multi-tenant support
Cloud storage integration
👨‍💻 Author

Kapil Nila

📜 License

MIT License
