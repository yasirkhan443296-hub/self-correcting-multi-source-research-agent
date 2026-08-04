<h1 align="center">🔍 Self-Correcting Multi-Source Research Agent</h1>

<p align="center">
  An advanced AI Research Agent built with <b>LangChain</b> that combines
  <b>Hybrid Retrieval</b>, <b>SQL</b>, <b>Live Web Search</b>,
  <b>Query Routing</b>, <b>Self-Critique</b>, and a
  <b>Retry Loop</b> to generate accurate, grounded, and reliable responses.
</p>

<hr>

<h2>📖 Project Overview</h2>

<p>
This project is a production-style AI Research Agent designed to answer complex
questions using multiple heterogeneous data sources. Instead of relying on a
single vector database, the system intelligently chooses between local documents,
a SQL database, and live web search depending on the user's query.
</p>

<p>
The application begins by loading documents from multiple formats including
PDF, CSV, and DOCX files. All documents are merged into a unified knowledge base,
split into semantic chunks, converted into vector embeddings using HuggingFace
Embeddings, and stored inside a FAISS vector database.
</p>

<p>
To improve retrieval quality, the system implements a Hybrid Retrieval strategy
by combining BM25 keyword search with FAISS semantic search through LangChain's
EnsembleRetriever. This enables the agent to retrieve both exact keyword matches
and semantically similar content for more accurate context retrieval.
</p>

<p>
Beyond document retrieval, the agent supports structured data by integrating a
SQL database capable of answering questions through automatically generated SQL
queries. It also includes live web search, allowing the system to retrieve
up-to-date information unavailable in local documents.
</p>

<p>
An intelligent Query Router analyzes every incoming question and automatically
selects the most appropriate knowledge source—Hybrid Retrieval, SQL Database,
or Web Search—before generating a response.
</p>

<p>
After generating an answer, the system performs a Self-Critique step where a
second LLM evaluates whether the response is fully supported by the retrieved
context. If the answer is not sufficiently grounded, the agent rewrites the
query, retrieves new context, regenerates the response, and repeats the
evaluation through a Retry Loop until a satisfactory answer is produced or the
maximum retry limit is reached.
</p>

<p>
The project also supports conversation memory for follow-up questions, structured
output generation, response streaming, and a modular architecture that separates
ingestion, retrieval, routing, generation, evaluation, memory, and orchestration
into independent components.
</p>

<hr>

<h2>✨ Key Features</h2>

<ul>
<li>📄 Multi-format Document Loading (PDF, DOCX, CSV)</li>
<li>✂️ Recursive Text Splitting</li>
<li>🤗 HuggingFace Embeddings</li>
<li>🗂️ FAISS Vector Database</li>
<li>🔍 BM25 Keyword Retrieval</li>
<li>⚡ Hybrid Retrieval (BM25 + FAISS)</li>
<li>🗄️ SQL Database Integration</li>
<li>🌐 Live Web Search</li>
<li>🧠 Intelligent Query Routing</li>
<li>💬 Context-Aware Answer Generation</li>
<li>🛡️ Self-Critique & Reflection</li>
<li>🔄 Automatic Retry Loop</li>
<li>📝 Structured Outputs</li>
<li>💭 Conversation Memory</li>
<li>📡 Streaming Responses</li>
<li>🏗️ Modular Production-Style Architecture</li>
</ul>

<hr>

<h2>🎯 Goal</h2>

<p>
The objective of this project is to demonstrate how modern AI systems can combine
multiple retrieval strategies, structured and unstructured data sources, intelligent
routing, and self-correction mechanisms to build reliable, production-ready AI
Research Agents capable of generating grounded and trustworthy responses.
</p>

<hr>

<p align="center">
⭐ If you find this project useful, consider giving it a star!
</p>
