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

# Document Portal - Interview Questions

This document contains a set of interview questions designed to assess a candidate's understanding of the Document Portal project. The questions range from high-level architectural concepts to specific implementation details within the RAG pipeline and API layer.

## Table of Contents

1.  [Architecture & Design](#1-architecture--design)
2.  [RAG Pipeline & Vector Stores](#2-rag-pipeline--vector-stores)
3.  [LangChain & Prompt Engineering](#3-langchain--prompt-engineering)
4.  [API & Backend Logic](#4-api--backend-logic)

---

## 1. Architecture & Design

### Question 1.1: Session Management

**Question:** The project heavily relies on a `session_id` for features like document chat. Could you explain the primary purpose of this session-based architecture and list two key benefits it provides?

**Answer:**
The primary purpose of the `session_id` is to **isolate user interactions and data**, creating a stateful and secure environment for each user.

**Key Benefits:**
1.  **Data Privacy and Isolation:** As seen in `ChatIngestor`, the `session_id` is used to create unique directories for uploaded files (`data/<session_id>`) and their corresponding vector indexes (`faiss_index/<session_id>`). This is a critical security feature that prevents one user's documents from being accessed or searched by another.
2.  **Stateful Conversations:** The RAG pipeline needs to understand conversational context (e.g., follow-up questions). The `session_id` allows the system to maintain a distinct chat history for each user. The `ConversationalRAG` class is initialized with a `session_id`, which is fundamental for its ability to rewrite questions based on past interactions within that specific session.

---

### Question 1.2: Project Modularity

**Question:** The project is organized into directories like `api`, `src`, `prompt`, and `utils`. What is the advantage of this structure, and how does it contribute to the project's maintainability?

**Answer:**
This modular structure follows the principle of **Separation of Concerns**, which is crucial for building scalable and maintainable applications.

*   **`api/`**: Contains only the API layer logic (FastAPI endpoints in `main.py`). This isolates web-related concerns from the core business logic.
*   **`src/`**: Holds the core application logic. It's further subdivided by feature (`document_chat`, `documentanalyzer`), making it easy to locate and modify the code for a specific piece of functionality without affecting others.
*   **`prompt/`**: Centralizes all LLM prompts in `prompt_library.py`. This is a best practice for LLM applications, as it allows for easy tuning, versioning, and management of prompts without changing the application code.
*   **`utils/`**: Contains reusable helper functions and classes (like `ModelLoader`) that are shared across different parts of the application, promoting code reuse and reducing duplication.

This separation makes the codebase easier to navigate, test, and debug. A developer can work on the RAG logic in `src/document_chat/retrieval.py` without needing to understand the intricacies of the FastAPI routing in `api/main.py`.

---

## 2. RAG Pipeline & Vector Stores

### Question 2.1: The Role of FAISS

**Question:** The project uses FAISS as a vector store. What is a vector store, and why is it a critical component of this RAG system? Walk me through how the `ChatIngestor` class prepares and uses it.

**Answer:**
A **vector store** is a specialized database designed to efficiently store and search high-dimensional vectors, which are numerical representations (embeddings) of text.

It's critical for a RAG system because it enables **fast semantic search**. Instead of keyword matching, it finds document chunks that are semantically similar to the user's query, providing highly relevant context to the LLM for generating an answer.

The `ChatIngestor` class in `src/document_ingestion/data_ingestion.py` uses it as follows:
1.  **File Handling:** It first saves the uploaded documents to a session-specific temporary directory.
2.  **Load & Split:** It uses `load_documents` to read the content and then a `RecursiveCharacterTextSplitter` to break the documents into smaller, manageable chunks.
3.  **Instantiate `FaissManager`:** It creates an instance of `FaissManager`, which is responsible for the low-level interaction with the FAISS index.
4.  **Embed & Index:** It passes the text chunks and their metadata to the `FaissManager`. The manager converts the text to embeddings and uses `FAISS.from_texts()` or `vs.add_documents()` to build or update the vector index, which is then saved to disk in the session's `faiss_dir`.

### Question 2.2: Idempotent Indexing

**Question:** In `src/document_ingestion/data_ingestion.py`, the `FaissManager` class has a `_fingerprint` method and checks if a key exists in its metadata before adding a new document. What is the purpose of this mechanism?

**Answer:**
This mechanism ensures **idempotent indexing**, meaning that the same document chunk will not be added to the vector store more than once, even if the user uploads the same file multiple times in a session.

*   The `_fingerprint` method creates a unique identifier for each document chunk based on its source and content hash.
*   The `add_documents` method checks this fingerprint against a stored metadata file (`ingested_meta.json`).
*   If the fingerprint already exists, the chunk is skipped.

This prevents the vector store from becoming bloated with duplicate data, which saves on storage, reduces embedding costs, and avoids skewed search results caused by redundant information.

---

## 3. LangChain & Prompt Engineering

### Question 3.1: Conversational Context

**Question:** The system needs to handle follow-up questions like "What about its architecture?". Looking at `prompt_library.py` and `retrieval.py`, explain the role of the `contextualize_question_prompt` and how the LCEL chain uses it.

**Answer:**
The `contextualize_question_prompt` is designed to solve the problem of **conversational ambiguity**. A vector store is stateless and cannot understand pronouns (like "its") or context from previous turns in a conversation.

**How it works in the LCEL chain:**
1.  **Rewrite the Question:** The `_build_lcel_chain` method in `ConversationalRAG` defines a `question_rewriter` chain. This is the *first step* in the pipeline.
2.  **Provide Context:** It passes the `chat_history` and the new `input` (the user's follow-up question) to an LLM using the `contextualize_question_prompt`.
3.  **Generate a Standalone Query:** The LLM's task is to rewrite the ambiguous follow-up question into a complete, standalone question. For example, "What about its architecture?" becomes "What is the architecture of the Transformer model from the 'Attention Is All You Need' paper?".
4.  **Improve Retrieval:** This clear, self-contained question is then passed to the retriever. This ensures the semantic search is performed on an unambiguous query, leading to much more accurate and relevant document retrieval.

### Question 3.2: The LCEL Chain

**Question:** In `src/document_chat/retrieval.py`, the `_build_lcel_chain` method constructs the main RAG pipeline. Can you describe the three main steps of this chain after the question has been contextualized?

**Answer:**
Yes, the chain in `ConversationalRAG` follows a classic "retrieve-then-read" pattern implemented with LangChain Expression Language (LCEL). After the initial question rewriting, the main steps are:

1.  **Retrieve (`retrieve_docs`):** The rewritten, standalone question is passed to the FAISS `retriever`. The retriever performs a similarity search and returns a set of relevant document chunks. The `_format_docs` utility function then concatenates their content into a single string.

2.  **Prepare for Generation:** The chain then constructs a dictionary containing the `context` (the retrieved documents), the original `input` (user question), and the `chat_history`.

3.  **Generate (`qa_prompt` | `llm`):** This dictionary is passed to the `context_qa_prompt`. This prompt instructs the LLM to act as a helpful assistant and answer the user's question *based only on the provided context*. The final output is parsed into a string using `StrOutputParser`.

This structured pipeline ensures the LLM is "grounded" by the retrieved documents, which minimizes hallucinations and provides answers based on the user's uploaded files.

---

## 4. API & Backend Logic

### Question 4.1: API Endpoint Logic

**Question:** In `api/main.py`, the `/chat/query` endpoint contains logic to check for `session_id` and verify that the index directory exists. Is this the best place for this logic? If you were to refactor it, where might you move it and why?

**Answer:**
While placing the logic in the endpoint works, it's not ideal from a separation of concerns perspective. The API endpoint's primary responsibility should be to handle HTTP requests/responses and delegate business logic, not perform file system checks.

**Refactoring Suggestion:**
This logic should be moved into the `ConversationalRAG` class, specifically within the `load_retriever_from_faiss` method.

*   The `load_retriever_from_faiss` method already accepts the `index_path`. It could be modified to perform the `os.path.isdir(index_path)` check at the beginning.
*   If the path doesn't exist, it should raise a specific, custom exception (e.g., `IndexNotFoundError`, a subclass of `DocumentPortalException`).
*   The FastAPI endpoint would then become much cleaner. It would simply call the method and use a `try...except` block to catch that specific exception, returning a 404 HTTP response to the user.

**Why this is better:**
*   **Encapsulation:** The `ConversationalRAG` class becomes fully responsible for its own dependencies (the FAISS index), making it more robust and self-contained.
*   **Reusability:** If another part of the system needed to use `ConversationalRAG`, it wouldn't have to reimplement the same validation logic.
*   **Cleaner API Layer:** The endpoint code in `main.py` becomes simpler and more focused on its core task of handling web traffic.

