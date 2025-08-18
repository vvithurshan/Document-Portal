# Document Portal

**Version: 0.0.1**

The Document Portal is a comprehensive FastAPI-based application designed to perform advanced operations on user-uploaded documents. It provides a suite of tools for document analysis, comparison, and interactive chat using a Retrieval-Augmented Generation (RAG) pipeline.

## Table of Contents

1.  [Project Overview](#project-overview)
2.  [Project Structure](#project-structure)
3.  [Core Features & Pipelines](#core-features--pipelines)
   *   [1. Document Analysis Pipeline](#1-document-analysis-pipeline)
   *   [2. Document Comparison Pipeline](#2-document-comparison-pipeline)
   *   [3. Conversational RAG Chat Pipeline](#3-conversational-rag-chat-pipeline)
4.  [Key Components](#key-components)
5.  [API Endpoints](#api-endpoints)
6.  [Setup and Running](#setup-and-running)

---

## Project Overview

This project is built to handle three primary use cases:

1.  **Analyze:** Extract structured information (like summaries, keywords, and sentiment) from a single document.
2.  **Compare:** Identify and list the differences between two documents on a page-by-page basis.
3.  **Chat:** Allow users to upload one or more documents and ask questions about their content. The system uses a RAG pipeline to provide context-aware answers.

A key architectural feature is **session management**. Each user interaction is isolated within a unique session (`session_id`), ensuring data privacy and stateful conversations. All uploaded files and generated vector indexes are stored in session-specific directories.

## Project Structure

The project is organized into a modular structure to separate concerns, making it easier to maintain and extend.

```
Document-Portal/
├── api/
│   └── main.py             # FastAPI application: endpoints and middleware.
├── data/
│   ├── document_analysis/  # Storage for files uploaded for analysis.
│   ├── document_compare/   # Storage for files uploaded for comparison.
│   └── ...                 # Default temp storage for chat documents.
├── faiss_index/            # Default storage for FAISS vector stores.
├── prompt/
│   └── prompt_library.py   # Central registry for all LLM prompts.
├── src/
│   ├── document_ingestion/
│   │   └── data_ingestion.py # Classes for document handling, ingestion, and FAISS management.
│   ├── documentanalyzer/
│   │   └── data_analysis.py  # Logic for the document analysis feature.
│   ├── documentcomparision/
│   │   └── doc_compare.py    # Logic for the document comparison feature.
│   └── document_chat/
│       └── retrieval.py      # Core RAG pipeline logic (ConversationalRAG).
├── static/                   # Static assets (CSS, JS) for the frontend.
├── templates/
│   └── index.html          # Jinja2 template for the web UI.
├── utils/
│   ├── model_loader.py     # Loads LLMs and embedding models.
│   ├── config_loader.py    # Loads YAML configuration.
│   └── ...                 # Other helper utilities.
├── test.py                   # Script for running integration tests.
└── README.md                 # This documentation file.
```

---

## Core Features & Pipelines

### 1. Document Analysis Pipeline

This pipeline extracts structured metadata from a single PDF.

**Endpoint:** `POST /analyze`

**Workflow:**

```
User Uploads PDF
      │
      ▼
[FastAPI Endpoint: /analyze]
      │
      ▼
[DocHandler]
  - Saves PDF to a session directory (e.g., data/document_analysis/<session_id>/)
  - Reads text content page by page.
      │
      ▼
[DocumentAnalyzer]
  - Receives the extracted text.
  - Uses an LLM with the `document_analysis_prompt`.
  - Formats the output into a structured JSON.
      │
      ▼
[JSON Response]
  - Returns the analysis (summary, keywords, etc.) to the user.
```

### 2. Document Comparison Pipeline

This pipeline compares two PDFs and highlights their differences.

**Endpoint:** `POST /compare`

**Workflow:**

```
User Uploads 2 PDFs (Reference & Actual)
      │
      ▼
[FastAPI Endpoint: /compare]
      │
      ▼
[DocumentComparator]
  - Saves both PDFs to a new session directory.
  - Reads and combines text from both files into a single context string.
      │
      ▼
[DocumentComparatorLLM]
  - Uses an LLM with the `document_comparison_prompt`.
  - Generates a page-wise comparison of the two documents.
      │
      ▼
[JSON Response]
  - Returns the comparison results to the user.
```

### 3. Conversational RAG Chat Pipeline

This is a two-stage pipeline that enables users to chat with their documents.

#### Stage A: Indexing

**Endpoint:** `POST /chat/index`

**Workflow:**

```
User Uploads 1+ Documents
      │
      ▼
[FastAPI Endpoint: /chat/index]
      │
      ▼
[ChatIngestor]
  - Saves files to a temporary session directory.
  - Loads document content (supports .pdf, .docx, .txt).
  - Splits documents into smaller, manageable chunks.
      │
      ▼
[FaissManager]
  - Creates text embeddings for each chunk using a sentence-transformer model.
  - Builds a FAISS vector index from the embeddings.
  - Saves the index to a persistent session directory (e.g., faiss_index/<session_id>/).
      │
      ▼
[JSON Response]
  - Returns the `session_id` to the user for subsequent queries.
```

#### Stage B: Querying

**Endpoint:** `POST /chat/query`

**Workflow:**

```
User sends Question + session_id
      │
      ▼
[FastAPI Endpoint: /chat/query]
      │
      ▼
[ConversationalRAG]
  - Loads the session-specific FAISS index.
  - **Step 1: Contextualize Question:** Rewrites the user's question using chat history to make it a standalone query (e.g., "what about it?" -> "what about the transformer architecture?").
  - **Step 2: Retrieve:** Performs a semantic search on the FAISS index with the rewritten question to find the most relevant document chunks.
  - **Step 3: Generate:** Passes the retrieved chunks (context), original question, and chat history to the LLM with the `context_qa_prompt`.
  - The LLM generates an answer based *only* on the provided context.
      │
      ▼
[JSON Response]
  - Returns the generated answer to the user.
```

---

## Key Components

*   **`api/main.py`**: The central nervous system of the application. It defines all API endpoints using FastAPI, handles request validation, and orchestrates calls to the backend logic in the `src` directory.
*   **`src/document_ingestion/data_ingestion.py`**: Contains the foundational classes for data handling.
    *   **`DocHandler`**: Manages saving and reading single PDFs for the analysis feature.
    *   **`DocumentComparator`**: Manages saving and combining two PDFs for the comparison feature.
    *   **`ChatIngestor`**: A robust class that handles the entire ingestion pipeline for the chat feature: saving files, loading content, splitting text, and building the vector store.
    *   **`FaissManager`**: A specialized utility to create, load, and update a FAISS vector store. It ensures that documents are not re-indexed if they already exist.
*   **`src/document_chat/retrieval.py`**:
    *   **`ConversationalRAG`**: The core of the chat functionality. It implements the "retrieve-then-read" logic using LangChain Expression Language (LCEL). It manages chat history, rewrites questions for clarity, and generates context-aware answers.
*   **`prompt/prompt_library.py`**: A crucial file that centralizes all prompts sent to the LLM. This makes it easy to experiment with and manage different prompt engineering strategies for each feature.

## API Endpoints

*   `GET /`: Serves the main HTML user interface.
*   `GET /health`: A simple health check endpoint.
*   `POST /analyze`: Upload a single PDF for analysis.
*   `POST /compare`: Upload two PDFs (`reference` and `actual`) for comparison.
*   `POST /chat/index`: Upload one or more documents to create a searchable vector index. Returns a `session_id`.
*   `POST /chat/query`: Ask a question against an indexed session using the `session_id`.

## Setup and Running

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Environment Variables:**
    Create a `.env` file in the project root and add your API keys:
    ```
    GOOGLE_API_KEY="your_google_api_key"
    LANGSMITH_API_KEY="your_langsmith_api_key" # Optional, for tracing
    LANGSMITH_PROJECT="your_project_name"     # Optional
    ```
3.  **Run the Application:**
    ```bash
    uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload
    ```
4.  **Access the UI:**
    Open your browser and navigate to `http://localhost:8080`.

