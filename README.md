# Omni-RAG-Engine

A lightweight, local Retrieval-Augmented Generation (RAG) engine built with FastAPI and LangChain. This application processes local PDF documents into structured text chunks, indexes them using a FAISS vector store, and provides context-aware conversational answers using Groq's high-speed inference.

## 🚀 Features

* **Local Document Ingestion**: Reads and parses text directly from uploaded PDFs.
* **Vector Architecture**: Uses `sentence-transformers/all-MiniLM-L6-v2` for generating local embeddings and FAISS for efficient similarity searches.
* **FastAPI Backend**: Clean asynchronous API endpoints for handling file uploads and streaming conversational queries.
* **Advanced Synthesis**: Integrated with `llama-3.3-70b-versatile` via Groq API for precise, context-bounded reasoning.

---

## 🛠️ Tech Stack

* **Framework**: FastAPI (Python 3.12+)
* **RAG Orchestration**: LangChain Core / Expression Language (LCEL)
* **Vector Database**: FAISS (Facebook AI Similarity Search)
* **LLM Provider**: Groq Cloud API
* **Frontend**: Vanilla HTML5 / JavaScript (Fetch API)

---

## 💻 Installation & Setup

Follow these steps to set up and run the application locally inside your environment (e.g., WSL Ubuntu or Linux).

### 1. Clone the Repository
```bash
git clone [https://github.com/ahb7/Omni-RAG-Engine.git](https://github.com/ahb7/Omni-RAG-Engine.git)
cd Omni-RAG-Engine
