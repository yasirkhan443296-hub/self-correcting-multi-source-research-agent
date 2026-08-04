import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_classic.chains import create_sql_query_chain
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, CSVLoader
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_classic.retrievers import EnsembleRetriever, BM25Retriever
from langchain_community.utilities import SQLDatabase
from langchain_community.tools import DuckDuckGoSearchResults

load_dotenv()

# ---------------- Pipeline functions ----------------

def load_pdf(p):
    return PyPDFLoader(p).load()

def load_csv(p):
    return CSVLoader(p).load()

def load_docx(p):
    return Docx2txtLoader(p).load()

def save_upload_file(uploaded_file):
    os.makedirs("temp", exist_ok=True)
    temp_path = os.path.join("temp", uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return temp_path

def create_text_splitting(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
    return splitter.split_documents(docs)

def create_embedding():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def create_vector_store(chunks, embeddings):
    vs = FAISS.from_documents(documents=chunks, embedding=embeddings)
    vs.save_local("faiss_index")
    return vs

def create_semantic_retriever(vectorstore, k=3):
    return vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": k})

def create_bm25_retriever(chunks, k=3):
    bm25 = BM25Retriever.from_documents(chunks)
    bm25.k = k
    return bm25

def create_hybrid_retriever(semantic_retriever, bm25_retriever, weights=(0.5, 0.5)):
    return EnsembleRetriever(retrievers=[semantic_retriever, bm25_retriever], weights=list(weights))

def load_database(db_path):
    return SQLDatabase.from_uri(f"sqlite:///{db_path}")

def create_sql_chain(llm, db):
    return create_sql_query_chain(llm, db)

def run_sql_query(question, sql_chain, db):
    sql_query = sql_chain.invoke({"question": question})
    try:
        result = db.run(sql_query)
    except Exception as e:
        result = f"SQL execution failed: {e}"
    return sql_query, result

def create_web_search_tool():
    return DuckDuckGoSearchResults()

def run_web_search(query, search_tool):
    try:
        return search_tool.invoke(query)
    except Exception as e:
        return f"Web search failed: {e}"

def create_query_router(llm):
    prompt = ChatPromptTemplate.from_template(
        """
You are a query routing assistant.
Decide which data source should answer the user's question.

1. hybrid - Questions about PDFs, DOCX, CSV files, research documents, general local knowledge
2. sql - Structured employee/company data: salary, department, experience, employee IDs, records
3. web - Latest news, current events, live information not likely in local documents

Return ONLY one word: hybrid, sql, or web.

Question:
{question}
"""
    )
    return prompt | llm | StrOutputParser()

def route_query(query, router):
    source = router.invoke({"question": query}).strip().lower()
    if source not in ("hybrid", "sql", "web"):
        source = "hybrid"
    return source

def format_context(source, raw_result):
    if source == "hybrid":
        return "\n\n".join(doc.page_content for doc in raw_result)
    return str(raw_result)

def execute_route(source, query, hybrid_retriever, sql_chain, db, search_tool):
    if source == "hybrid":
        docs = hybrid_retriever.invoke(query)
        return "hybrid", docs, format_context("hybrid", docs)
    elif source == "sql":
        if db is None or sql_chain is None:
            docs = hybrid_retriever.invoke(query)
            return "hybrid (sql unavailable)", docs, format_context("hybrid", docs)
        sql_query, result = run_sql_query(query, sql_chain, db)
        return "sql", result, f"SQL Query: {sql_query}\nResult: {result}"
    elif source == "web":
        result = run_web_search(query, search_tool)
        return "web", result, format_context("web", result)
    else:
        raise ValueError(f"Unknown source: {source}")

def create_answer_chain(llm):
    prompt = ChatPromptTemplate.from_template(
        """
You are an AI Research Assistant.
Answer the user's question ONLY using the provided context.
If the answer is not in the context, say: "I don't have enough information to answer this."

Conversation History:
{chat_history}

Context:
{context}

Question:
{question}
"""
    )
    return prompt | llm | StrOutputParser()

def generate_answer(question, context, chat_history, answer_chain):
    return answer_chain.invoke({"question": question, "context": context, "chat_history": chat_history})

def create_critique_chain(llm):
    prompt = ChatPromptTemplate.from_template(
        """You are an AI evaluator. Evaluate whether the answer is supported by the provided context.

Context:
{context}

Question:
{question}

Answer:
{answer}

Return ONLY one word.
PASS -> if the answer is fully supported.
FAIL -> if the answer is incorrect, hallucinated, or not supported by the context.
"""
    )
    return prompt | llm | StrOutputParser()

def evaluate_answer(question, context, answer, critique_chain):
    verdict = critique_chain.invoke({"question": question, "context": context, "answer": answer})
    return verdict.strip().lower()

def create_rewrite_chain(llm):
    prompt = ChatPromptTemplate.from_template(
        """
The following question did not receive a well-supported answer from the retrieved context.
Rewrite it to be clearer and more specific. Return ONLY the rewritten question.

Original Question:
{question}
"""
    )
    return prompt | llm | StrOutputParser()

def answer_with_self_correction(query, chat_history, router, hybrid_retriever, sql_chain, db,
                                 search_tool, answer_chain, critique_chain, rewrite_chain, max_retries=2):
    current_query = query
    attempts = []
    source_used, context_text, answer = None, "", ""

    for attempt in range(max_retries + 1):
        source_used = route_query(current_query, router)
        _, _, context_text = execute_route(source_used, current_query, hybrid_retriever, sql_chain, db, search_tool)
        answer = generate_answer(current_query, context_text, chat_history, answer_chain)
        verdict = evaluate_answer(current_query, context_text, answer, critique_chain)
        attempts.append({"attempt": attempt + 1, "query": current_query, "source": source_used, "verdict": verdict})

        if verdict == "pass":
            return {"answer": answer, "source": source_used, "context": context_text,
                    "attempts": attempts, "grounded": True}
        if attempt < max_retries:
            current_query = rewrite_chain.invoke({"question": current_query}).strip()

    return {"answer": answer, "source": source_used, "context": context_text,
            "attempts": attempts, "grounded": False}

def get_session_history(session_id):
    if session_id not in st.session_state.history_store:
        st.session_state.history_store[session_id] = InMemoryChatMessageHistory()
    return st.session_state.history_store[session_id]

def format_chat_history(history, max_turns=5):
    messages = history.messages[-(max_turns * 2):]
    lines = [f"{'User' if m.type == 'human' else 'Assistant'}: {m.content}" for m in messages]
    return "\n".join(lines) if lines else "(no previous conversation)"

def initialize_pipeline(pdf_paths, csv_paths, docx_paths, db_path):
    api_key = os.getenv("GROQ_API_KEY")
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3, api_key=api_key)

    all_documents = []
    for p in pdf_paths:
        all_documents.extend(load_pdf(p))
    for p in csv_paths:
        all_documents.extend(load_csv(p))
    for p in docx_paths:
        all_documents.extend(load_docx(p))

    chunks = create_text_splitting(all_documents)
    embeddings = create_embedding()
    vectorstore = create_vector_store(chunks, embeddings)

    semantic_retriever = create_semantic_retriever(vectorstore)
    bm25_retriever = create_bm25_retriever(chunks)
    hybrid_retriever = create_hybrid_retriever(semantic_retriever, bm25_retriever)

    db, sql_chain = None, None
    if db_path and os.path.exists(db_path):
        db = load_database(db_path)
        sql_chain = create_sql_chain(llm, db)

    search_tool = create_web_search_tool()
    router = create_query_router(llm)
    answer_chain = create_answer_chain(llm)
    critique_chain = create_critique_chain(llm)
    rewrite_chain = create_rewrite_chain(llm)

    return {
        "doc_count": len(all_documents), "chunk_count": len(chunks),
        "hybrid_retriever": hybrid_retriever, "sql_chain": sql_chain, "db": db,
        "search_tool": search_tool, "router": router, "answer_chain": answer_chain,
        "critique_chain": critique_chain, "rewrite_chain": rewrite_chain,
    }

def run_agent(query, session_id, pipeline, max_retries=2):
    history = get_session_history(session_id)
    chat_history_text = format_chat_history(history)
    result = answer_with_self_correction(
        query=query, chat_history=chat_history_text, router=pipeline["router"],
        hybrid_retriever=pipeline["hybrid_retriever"], sql_chain=pipeline["sql_chain"],
        db=pipeline["db"], search_tool=pipeline["search_tool"], answer_chain=pipeline["answer_chain"],
        critique_chain=pipeline["critique_chain"], rewrite_chain=pipeline["rewrite_chain"],
        max_retries=max_retries
    )
    history.add_user_message(query)
    history.add_ai_message(result["answer"])
    return result

# ---------------- Streamlit UI ----------------

def main():
    st.set_page_config(page_title="Agentic Multi-Source RAG", page_icon="\U0001F9E0", layout="wide")
    st.title("\U0001F9E0 Agentic Multi-Source RAG")
    st.caption("Hybrid retrieval (BM25 + FAISS) - SQL - Web search - Self-critique - Retry loop - Memory")

    if not os.getenv("GROQ_API_KEY"):
        st.warning("GROQ_API_KEY is not set. Add it to your .env file before processing documents.")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "history_store" not in st.session_state:
        st.session_state.history_store = {}
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = None

    with st.sidebar:
        st.subheader("1. Upload sources")
        pdf_files = st.file_uploader("PDF documents", type=["pdf"], accept_multiple_files=True)
        csv_files = st.file_uploader("CSV documents", type=["csv"], accept_multiple_files=True)
        docx_files = st.file_uploader("DOCX documents", type=["docx"], accept_multiple_files=True)
        db_file = st.file_uploader("SQLite database (optional)", type=["db"])

        process = st.button("\U0001F680 Process Documents")

        st.divider()
        max_retries = st.slider("Max self-correction retries", 0, 3, 2)

        if st.button("\U0001F5D1\uFE0F Clear chat"):
            st.session_state.messages = []
            st.session_state.history_store = {}
            st.rerun()

    if process:
        if not (pdf_files or csv_files or docx_files):
            st.warning("Please upload at least one PDF, CSV, or DOCX document to process.")
        else:
            with st.spinner("Processing documents and building the pipeline..."):
                pdf_paths = [save_upload_file(f) for f in (pdf_files or [])]
                csv_paths = [save_upload_file(f) for f in (csv_files or [])]
                docx_paths = [save_upload_file(f) for f in (docx_files or [])]
                db_path = save_upload_file(db_file) if db_file else None

                st.session_state.pipeline = initialize_pipeline(pdf_paths, csv_paths, docx_paths, db_path)
            st.success(
                f"Processed {st.session_state.pipeline['doc_count']} documents "
                f"into {st.session_state.pipeline['chunk_count']} chunks."
            )

    if st.session_state.pipeline:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message.get("meta"):
                    st.caption(message["meta"])

        query = st.chat_input("Ask a question...")
        if query:
            st.session_state.messages.append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.markdown(query)

            try:
                with st.spinner("Thinking..."):
                    result = run_agent(query, "user1", st.session_state.pipeline, max_retries=max_retries)

                retries_used = len(result["attempts"]) - 1
                grounded_label = "\u2705 grounded" if result["grounded"] else "\u26A0\uFE0F not fully grounded after retries"
                meta = f"Source: {result['source']} | Retries: {retries_used} | {grounded_label}"

                with st.chat_message("assistant"):
                    st.markdown(result["answer"])
                    st.caption(meta)
                    with st.expander("View retrieved context / attempts"):
                        st.write(result["context"])
                        st.json(result["attempts"])

                st.session_state.messages.append({"role": "assistant", "content": result["answer"], "meta": meta})

            except Exception as e:
                st.error(f"Error: {e}")
    else:
    st.markdown("""
    ## 🚀 Welcome to Agentic Multi-Source RAG

    An intelligent AI Research Assistant that can answer questions from
    multiple data sources using an agentic workflow.

    ### ✨ Key Features

    ✅ Hybrid Search (FAISS + BM25)

    ✅ Intelligent Query Router
    - PDF / DOCX / CSV
    - SQLite Database
    - Web Search

    ✅ Conversational Memory

    ✅ Self-Correction & Retry Loop

    ✅ Grounded Answers

    ✅ Automatic Source Selection

    ---

    ### 📂 Supported Files

    • PDF Documents

    • DOCX Documents

    • CSV Files

    • SQLite Databases

    ---

    ### ⚙️ How it Works

    1. Upload your documents.
    2. Click **Process Documents**.
    3. Ask questions in natural language.
    4. The AI automatically selects the best source.
    5. Answers are verified before being returned.

    ---
    **Built with:** LangChain • Groq • FAISS • BM25 • Streamlit • DuckDuckGo • SQLite
    """)

if __name__ == "__main__":
    main()
