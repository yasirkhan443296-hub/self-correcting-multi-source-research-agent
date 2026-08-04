<div align="center">

# 🔍 Self-Correcting Multi-Source Research Agent

### 🚀 Production-Ready AI Research Agent using LangChain, Hybrid Retrieval, SQL, Web Search & Reflection

<img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge"/>
<img src="https://img.shields.io/badge/LangChain-AI-success?style=for-the-badge"/>
<img src="https://img.shields.io/badge/FAISS-VectorDB-orange?style=for-the-badge"/>
<img src="https://img.shields.io/badge/HuggingFace-Embeddings-yellow?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Streamlit-Deployed-red?style=for-the-badge"/>

</div>

---

# 📖 About The Project

Unlike traditional RAG chatbots that depend on a single vector database, this project implements a complete **production-style AI Research Agent** capable of retrieving information from **multiple heterogeneous data sources**, evaluating its own responses, and automatically improving answers whenever the retrieved evidence is insufficient.

The application follows a modular AI engineering architecture where every component is implemented independently—from document ingestion and hybrid retrieval to intelligent routing, answer generation, self-evaluation, retry mechanisms, conversation memory, and an interactive Streamlit interface.

---

# ⚙️ Complete Development Workflow

## 🟢 Phase 1 — Project Initialization

✔ Created a clean production-ready project structure.

✔ Installed all required dependencies.

✔ Configured environment variables using **python-dotenv**.

✔ Initialized the Large Language Model.

✔ Configured API keys securely.

---

## 📚 Phase 2 — Document Ingestion

Implemented loaders for multiple document formats:

📄 PDF Documents

📑 DOCX Documents

📊 CSV Files

Every document is loaded independently before being merged into one unified knowledge base.

---

## 📄 Phase 3 — Document Processing

All loaded documents are combined into a single collection.

The application then uses **RecursiveCharacterTextSplitter** to divide large documents into overlapping semantic chunks that preserve contextual information for retrieval.

---

## 🤗 Phase 4 — Embedding Generation

Each document chunk is converted into high-dimensional vector embeddings using **HuggingFace Embeddings**, allowing semantic similarity search instead of simple keyword matching.

---

## 🗂 Phase 5 — Vector Database

Generated embeddings are stored inside a **FAISS Vector Store**.

The project includes functionality to:

✔ Create Vector Store

✔ Save Vector Store

✔ Load Existing Vector Store

This avoids rebuilding embeddings every time the application starts.

---

## 🔍 Phase 6 — Semantic Retrieval

Implemented a FAISS Retriever capable of retrieving semantically relevant document chunks based on the user's question.

Instead of exact keyword matching, the retriever understands contextual meaning.

---

## 📖 Phase 7 — Keyword Retrieval

Implemented **BM25 Retriever** for lexical search.

BM25 excels when the user's query contains exact terminology or technical keywords that should be matched precisely.

---

## ⚡ Phase 8 — Hybrid Retrieval

Built an **EnsembleRetriever** combining:

• BM25 Retrieval

• FAISS Semantic Retrieval

The hybrid retriever balances keyword precision with semantic understanding to significantly improve retrieval quality.

---

## 🗄 Phase 9 — SQL Database Integration

Integrated a SQL database capable of answering questions from structured information.

Implemented:

✔ SQL Database Connection

✔ Natural Language → SQL Query Generation

✔ SQL Query Execution

This allows the agent to answer analytical questions directly from database records.

---

## 🌐 Phase 10 — Live Web Search

Integrated live web search allowing the assistant to retrieve recent or external information unavailable inside local documents.

This enables the agent to answer questions involving current events or missing knowledge.

---

## 🧠 Phase 11 — Intelligent Query Routing

Developed an LLM-powered Query Router.

For every user question, the router automatically determines whether the answer should come from:

📄 Hybrid Retriever

🗄 SQL Database

🌐 Live Web Search

The user never needs to manually choose the information source.

---

## 💬 Phase 12 — Answer Generation

Retrieved context is passed to a dedicated Answer Generation Chain.

The LLM is instructed to answer **only using the retrieved evidence**, minimizing hallucinations and improving factual accuracy.

---

## 🛡 Phase 13 — Self-Critique

Implemented a Reflection Chain.

After producing an answer, a second LLM evaluates:

✔ Is the answer supported by retrieved evidence?

✔ Is the response grounded?

✔ Is there any hallucination?

Only validated responses are accepted.

---

## 🔄 Phase 14 — Retry Mechanism

If the answer fails evaluation:

✔ Rewrite User Query

✔ Retrieve Better Context

✔ Generate New Answer

✔ Re-evaluate

The process repeats automatically until either:

✅ A grounded response is generated

or

🚫 Maximum retry limit is reached.

---

## 💭 Phase 15 — Conversation Memory

Implemented conversation history using **RunnableWithMessageHistory**.

Users can ask natural follow-up questions without repeating previous context.

---

## 📑 Phase 16 — Structured Outputs

Generated responses are returned in structured format including:

• Final Answer

• Confidence

• Source References

This makes downstream integrations significantly easier.

---

## ⚡ Phase 17 — Streaming Responses

Implemented token-by-token streaming for faster response generation and an improved user experience.

---

## 🎨 Phase 18 — Streamlit User Interface

Developed a complete Streamlit application featuring:

📂 Multi-file Upload

💬 Interactive Chat Interface

📚 Conversation History

⚡ Streaming Responses

🔍 Source Display

🧠 Intelligent Multi-Source Retrieval

---

# 🏗 System Architecture

```text
User Question
      │
      ▼
Query Router
      │
 ┌────┼────┐
 ▼    ▼    ▼
Hybrid SQL Web
  │     │    │
  └─────┼────┘
        ▼
Retrieved Context
        ▼
Answer Generation
        ▼
Self Critique
        │
   PASS / FAIL
        │
        ▼
Retry Loop
        ▼
Structured Output
        ▼
Conversation Memory
        ▼
Streaming Response
        ▼
Streamlit Interface
