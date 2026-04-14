# 🏭 Volta: Agentic RAG for B2B Industrial Automation Sales

![Architecture](https://img.shields.io/badge/Architecture-Agentic_RAG-orange)
![Extraction](https://img.shields.io/badge/Extraction-Docling_%2B_Pydantic-blue)
![Database](https://img.shields.io/badge/VectorDB-Qdrant-red)
![Deployment](https://img.shields.io/badge/Deployment-Docker_Compose-brightgreen)

## 📌 The Business Bottleneck
In the industrial automation sector (B2B), technical sales engineers spend hours digging through dense, hundreds-of-pages-long PDF catalogs to match client requirements with exact sensor specifications (e.g., *LiDAR range, IMU frequency, Encoder resolution*). 

Traditional RAG (Retrieval-Augmented Generation) systems fail at this because naive chunking algorithms destroy tabular data and mix up specifications across different product families.

## 💡 The Volta Solution
Volta is a **Precision-First Agentic RAG** system designed specifically for industrial sensor catalogs. Instead of unstructured text retrieval, Volta utilizes layout-aware extraction to map complex catalog data into strict, strongly-typed schemas (Lidar, IMU, Encoders, ToF, etc.), powering an autonomous sales agent capable of consulting and handling quotes.

## ⚙️ Core Architecture

### 1. Deterministic Extraction Pipeline (`src/extraction/`)
- **Layout-Aware Parsing:** Uses `Docling` (`docling_extractor.py`) to parse complex PDFs, keeping tables and product families intact.
- **Strict Data Validation:** Extracted data is routed (`handler.py`) and validated against domain-specific Pydantic schemas:
  - 📡 `lidar.py` / `tof.py`
  - 🧭 `imu.py` / `encoder.py`
  - 💨 `air_quality.py` / `oil_sensor.py`
- This ensures the LLM never hallucinates technical limits like operating voltage or IP ratings.

### 2. Dual-Memory System (`src/database/` & `src/memory/`)
- **Semantic Search:** `Qdrant` (`qdrant_core.py`) stores vector embeddings for fuzzy, intent-based queries (e.g., *"sensors for harsh environments"*).
- **Persistent State:** `redis_core.py` and `persistent_memory.py` manage conversation history and session states, allowing multi-turn technical consultations.

### 3. ReAct Agent Engine (`src/ai/`)
Powered by LangGraph, the main `agent.py` acts as a routing brain equipped with specific business tools:
- 🔍 `catalog_search.py`: Queries Qdrant and filters through structured Pydantic records to find exact technical matches.
- 💰 `quote_handler.py`: Generates and manages preliminary technical quotations based on the user's selected components.

## 🗂️ Project Structure

```text
b2b-sale-rag/
├── data/
│   └── raw_pdfs/            # Original manufacturer B2B catalogs
├── scripts/
│   └── run_pipeline.py      # Entry point for the ETL & Indexing pipeline
├── src/
│   ├── ai/                  # LangGraph Agent, Embedder, and Tool definitions
│   ├── api/                 # FastAPI entry points (main.py)
│   ├── database/            # Qdrant integration and Persistent Memory setup
│   ├── extraction/          # Docling extraction, mapping logic, and strict Schemas
│   └── memory/              # Redis core for session handling
├── Dockerfile               # Containerization for the API and Agent
├── docker-compose.yml       # Orchestrates App, Qdrant, and Redis
└── requirements.txt
```

🚀 Quick Start
Prerequisites
Docker & Docker Compose

API Keys for your chosen LLM (OpenAI/Anthropic) populated in .env

**1. Spin up the infrastructure**
Start the API, Qdrant Vector DB, and Redis instances via Docker:
```
Bash
docker-compose up -d
```
**2. Run the Data Pipeline**
Ingest the industrial catalogs from data/raw_pdfs, extract schemas via Docling, and populate Qdrant:
```
```Bash```
python scripts/run_pipeline.py
```
**3. Access the Agent**
The FastAPI server exposes the agent endpoints.
API Docs: http://localhost:8000/docs

**🛠️ Tech Stack**
Extraction: Docling, Pydantic
- Agent Framework: LangChain / LangGraph
- Vector Store: Qdrant
- Memory/Cache: Redis
- Backend: FastAPI, Python 3.10+
- Infra: Docker
