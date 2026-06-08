# OSSify 🚀

**Contributor-Centric Repository Intelligence Platform**

OSSify is an AI-powered repository analysis platform that automatically discovers contributor expertise, builds repository knowledge graphs, enables semantic repository search, and generates Contributor Digital Twins for intelligent developer assistance.

---

## ✨ Features

### 📊 Repository Analysis

* Analyze any public GitHub repository
* Extract commits, pull requests, issues, and contributors

### 👨‍💻 Contributor Expertise Discovery

* Identify domain experts across the repository

* Expertise classification across areas such as:

  * Frontend
  * Backend
  * Database
  * DevOps
  * Testing
  * Documentation

* Confidence-based expert ranking

* Semantic expert search

### 🧠 Contributor-Centric RAG

* Repository knowledge indexed into a vector database
* Semantic retrieval using embeddings
* Context-aware contributor expertise lookup

Example queries:

> Who is the expert in authentication?

> Who works most on routing?

> Who should review Flask session bugs?

### 🕸️ Knowledge Graph Generation

OSSify automatically constructs a repository knowledge graph connecting:

* Repositories
* Topics
* Contributors
* Expertise Domains

The graph enables visual exploration of repository knowledge and contributor relationships.

### 🤖 Contributor Digital Twin

Generate an AI-powered digital representation of contributors using:

* Commit history
* Pull requests
* Issues
* Repository activity
* Expertise signals

The Digital Twin can answer repository-specific questions using contributor knowledge.

### 💬 Ask AI

Interactive expert discovery assistant that allows users to:

* Search experts by topic
* Discover contributor expertise
* Find the best reviewer for a feature or issue
* Explore repository knowledge using natural language

---

# 🏗️ System Architecture

```text
GitHub Repository
        │
        ▼
Data Ingestion Pipeline
(Commits, PRs, Issues)
        │
        ▼
PostgreSQL Storage
        │
 ┌──────┴──────┐
 ▼             ▼
Neo4j       Qdrant
(Graph)     (Vector DB)
 │             │
 ▼             ▼
Knowledge   Semantic
 Graph      Retrieval
 │             │
 └──────┬──────┘
        ▼
 Contributor-Centric RAG
        ▼
 Digital Twin & Expert Search
        ▼
 Frontend Dashboard
```

---

# ⚙️ Tech Stack

## Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS

## Backend

* FastAPI
* SQLAlchemy
* PostgreSQL

## AI & Retrieval

* Sentence Transformers

  * all-MiniLM-L6-v2
* Qdrant Vector Database
* Groq LLM

## Knowledge Graph

* Neo4j

## External APIs

* GitHub REST API
* Groq API
* ElevenLabs API

---

# 📂 Project Structure

```text
OSSify/
    ├── README.md
    ├── LICENSE
    ├── requirements.txt
    ├── VOICE_DIGITAL_TWIN_GUIDE.md
    ├── backend/
    │   └── app/
    │       ├── main.py
    │       ├── api/
    │       ├── db/
    │       ├── models/
    │       ├── services/
    │       └── tasks/
    ├── data_pipeline/
    │   ├── extract/
    │   ├── load/
    │   └── utils/
    ├── frontend/
    │   └── src/
    │       ├── app/
    │       ├── components/
    │       └── lib/
    ├── graph/
    │   └── builders/
    └── rag_pipeline/
        ├── run_builder.py
        ├── run_extractor.py
        ├── api/
        ├── documents/
        ├── embeddings/
        ├── extraction/
        ├── indexing/
        ├── rag/
        ├── retrieval/
        ├── utils/
        └── vector_store/
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/ShreshthaAggarwal27/OSSify.git
cd OSSify
```

---

## Backend Setup

Create virtual environment:

```bash
python -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

or on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start backend:

```bash
uvicorn app.main:app --reload
```

---

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

# 🔐 Environment Variables

Create a `.env` file:

```env
GITHUB_TOKEN=

DATABASE_URL=

QDRANT_URL=

QDRANT_API_KEY=

NEO4J_URI=
NEO4J_USER=
NEO4J_PASSWORD=

GROQ_API_KEY=

ELEVENLABS_API_KEY=
```

---

# 📈 Example Workflow

### Step 1

Add a GitHub repository URL.

### Step 2

OSSify fetches:

* Contributors
* Commits
* Pull Requests
* Issues

### Step 3

Repository knowledge is stored in:

* PostgreSQL
* Neo4j
* Qdrant

### Step 4

Expertise scores are computed.

### Step 5

Knowledge Graph and Contributor Digital Twins are generated.

### Step 6

Users explore repository knowledge through the dashboard and Ask AI assistant.

---

# 📊 Evaluation Snapshot

Repository Used:

* pallets/flask

Statistics:

* 67 Contributors
* 267 Files
* 6 Expertise Domains
* Hundreds of commits, PRs, and issues processed

Performance Metrics:

* Precision@K
* Retrieval Accuracy
* Response Latency
* Knowledge Graph Statistics

---

# 🔮 Future Enhancements

* Multi-repository analysis
* Advanced contributor recommendations
* Automatic code reviewer assignment
* Repository health scoring
* Temporal expertise tracking
* Multi-modal Digital Twins
* Voice-based contributor interaction
* Real-time GitHub webhook integration

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/new-feature
```

3. Commit changes

```bash
git commit -m "feat: add new feature"
```

4. Push changes

```bash
git push origin feature/new-feature
```

5. Open a Pull Request

---

# 📜 License

This project is licensed under the MIT License.

---

# 👥 Authors

- **Vaishnavi Singh**
- **Shreshtha Aggarwal**

Contributor-Centric Repository Intelligence using Knowledge Graphs, RAG, and Digital Twins.
