# Secure Enterprise Knowledge Assistant

An AI-powered enterprise knowledge retrieval platform that enables secure querying across PDFs, CSVs, JSON logs, and structured enterprise datasets using Retrieval-Augmented Generation (RAG).

## Features

- Multi-source ingestion
- Hybrid Retrieval (FAISS + BM25)
- Cross-Encoder Re-ranking
- Role-Based Access Control (RBAC)
- Query Routing
- Explainable Citations
- Confidence Scoring
- Audit Logging
- Streamlit Dashboard

A technically strong, practical, and understandable Secure Enterprise Knowledge Assistant with strict Role-Based Access Control (RBAC) and a lightweight agent-inspired workflow where a router directs queries to domain-specific retrieval logic. Designed as an AIML Capstone project.

> **Project Explanation Statement:**
> Developed a production-grade Secure Enterprise Knowledge Assistant supporting multi-source enterprise data ingestion (PDF, CSV, JSON, SQL), Hybrid Retrieval (FAISS + BM25), Role-Based Access Control, Query Routing, explainable Citations, Confidence Scoring, audit logging, and hallucination mitigation. The system enforces RBAC before retrieval, ensuring restricted content never enters the generation context. The RAG Pipeline provides secure, grounded, and traceable responses suitable for enterprise environments.

---

## 🎨 System Design & Architecture

![System Architecture](architecture.png)

The system coordinates security and intelligence across a lightweight agent-inspired workflow where a router directs queries to domain-specific retrieval logic, using Hybrid Retrieval and a Cross-Encoder Reranker:

```mermaid
graph TD
    User([User Query]) --> Auth[JWT & RBAC Session Check]
    Auth --> Router[Query Router Logic]
    
    subgraph Specialist Retrieval Logic (Metadata Filtered)
        Router -- HR Query --> HR_Retrieval[HR Specialist Retrieval]
        Router -- Finance Query --> Fin_Retrieval[Finance Specialist Retrieval]
        Router -- Security Query --> Sec_Retrieval[Security Specialist Retrieval]
        Router -- General Query --> Gen_Retrieval[General Specialist Retrieval]
    end
    
    HR_Retrieval --> Retrieve[Hybrid Search: FAISS + BM25]
    Fin_Retrieval --> Retrieve
    Sec_Retrieval --> Retrieve
    Gen_Retrieval --> Retrieve
    
    Retrieve --> Rerank[Cross-Encoder Reranker]
    Rerank --> Guard[Hallucination Guard / Confidence Check]
    
    Guard -- Confidence < Threshold --> Insufficient[Return: Insufficient Evidence Found]
    Guard -- Confidence >= Threshold --> Synthesizer[Response Synthesizer]
    
    Synthesizer --> GroundCheck[Groundedness Verification Layer]
    GroundCheck -- Passes --> FinalResponse[Traceable Answer + Citations]
    GroundCheck -- Fails --> SafetyMitigation[Safety Alert Response]
    
    FinalResponse --> Audit[Log to SQLite Audit Database]
    Insufficient --> Audit
```

---

## 💡 Design Choices & Trade-offs

1. **Consolidated Backend (`main.py`)**:
   - **Choice**: All backend logic (FastAPI endpoints, SQLite DB helper, parser chunkers, FAISS search, and routing workflow) is written inside `main.py`.
   - **Trade-off**: This violates standard enterprise modularity (where each component is a separate service or package), but it keeps the project cohesive, prevents circular import issues with machine learning models, and makes local deployment and debugging extremely simple.
   - **Interview Explanation**: "Consolidating the backend allowed us to keep the deployment footprint small and avoid the overhead of microservice communication during development, though in a real-world enterprise setting, we would split these into a dedicated Ingestion Service, Auth Server, and Vector Search Service."

2. **Pre-Retrieval Metadata Filtering**:
   - **Choice**: Security clearance is checked *before* executing the search. A SQL query resolves authorized document IDs, which are passed as a metadata filter lambda directly into the FAISS index search.
   - **Trade-off**: Ensures unauthorized document chunks never leak into the retrieval context. However, pulling all allowed document IDs first scales linearly with the document count.
   - **Interview Explanation**: "By applying the filter during the index search rather than post-filtering, we guarantee restricted context never enters the LLM generation prompt. For scaling to millions of files, we would swap FAISS for a managed vector database (like Qdrant or Milvus) that natively handles hierarchical role partition indexes."

3. **Local CPU Inference for RAG**:
   - **Choice**: Runs `sentence-transformers` embeddings (`all-MiniLM-L6-v2`) and Cross-Encoder re-ranker (`ms-marco-MiniLM-L-6-v2`) locally on the CPU, with a fallback Mock LLM.
   - **Trade-off**: Free, completely offline, and keyless setup, but introduces a 1-2 second latency per query.
   - **Interview Explanation**: "Using local sentence-transformers models makes the system self-contained and free. In a production pipeline, we would host these models on a GPU-accelerated server like Triton Inference Server or vLLM to achieve sub-100ms latency."

4. **Web Audio API Sound Engine**:
   - **Choice**: UI sound effects are synthesized dynamically in the browser using the JavaScript Web Audio API.
   - **Trade-off**: No static MP3 files to load or host, but limited to synthesized retro square/sine wave sound effects.
   - **Interview Explanation**: "Dynamic browser synthesis ensures audio effects always play reliably without breaking due to static file path resolution issues in web containers."

---

## 🚧 Challenges Faced & Resolved

1. **Tabular Data & Log Ingestion**:
   - *Problem*: Passing raw CSV files or JSON log dumps to a vector database resulted in poor semantic retrieval because the vector model didn't understand row relationships.
   - *Resolution*: We developed parser pre-processors that convert structured data rows into descriptive English sentences (e.g. converting a CSV row into: `Row 3 in sales_records.csv: TransactionID: TX1003, Client: Apex, Amount: 150000`) before vectorizing.
2. **FAISS Lambda Filtering**:
   - *Problem*: Standard FAISS does not support flexible SQL-like metadata queries easily.
   - *Resolution*: We implemented a metadata filter callable that intercepts FAISS node evaluations: `filter=lambda metadata: metadata.get("document_id") in allowed_ids`.

---

## ⚠️ Known Limitations

- **Keyword-Assisted Routing**: Query routing is keyword-assisted and can be improved using LLM-based intent classification.
- **FAISS Scaling**: FAISS metadata filtering works well for small datasets but would require a more scalable document permission architecture for enterprise-scale deployments.
- **CPU Inference Latency**: Local embedding and re-ranking models increase latency compared to dedicated GPU-hosted inference services.
- **Synthetic Datasets**: The current system runs on synthetic data generated for demonstration purposes.

---

## ⚙️ Future Enhancements (TODOs)

- [ ] **Hierarchical Chunking**: Replace the sliding character window with an AST or markdown-header-aware parser to improve chunk coherence.
- [ ] **GPU Acceleration**: Add support for CUDA GPU detection to accelerate embeddings and re-ranking.
- [ ] **OAuth2/Okta Integration**: Replace the SQLite user account table with Okta/Auth0 or Active Directory LDAP for corporate SSO.
- [ ] **Multi-turn Chat Memory**: Add thread memory using a sliding window context or summary buffer.

---

## 🛠️ Local Installation & Run Guide

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Seed & Boot the Backend
The backend automatically runs the dataset generator on first boot. If you want to run it manually:
```bash
python generate_dataset.py
```
Then start the server:
```bash
python main.py
```
FastAPI runs at `http://localhost:8000`.

### Step 3: Start the Streamlit Dashboard
```bash
streamlit run app.py
```
Streamlit runs at `http://localhost:8501`.

### Step 4: Run Tests
```bash
pytest tests/test_platform.py -v
```

---

## 👥 Demo Profiles
Use the **Quick Demo Profiles** tab on the login screen to quickly switch clearances:

| Username | Password | Role | Department | Clearance Scope |
|---|---|---|---|---|
| **admin** | `admin123` | **Admin** | General | Access to ALL documents, user lists, metrics, and logs. |
| **alice** | `alice123` | **HR** | HR | HR handbooks, employee directories, public files. |
| **bob** | `bob123` | **Finance** | Finance | Sales records, revenue reports. |
| **charlie** | `charlie123` | **Engineering** | Engineering | Coding guidelines, repository architectures. |
| **david** | `david123` | **Compliance** | Security | Compliance reports, security audit logs, performance traces. |
