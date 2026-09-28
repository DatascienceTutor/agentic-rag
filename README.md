# Enterprise Agentic RAG

An Enterprise Retrieval-Augmented Generation (RAG) assistant built with **Streamlit**, **LangChain/LangGraph**, **OpenAI**, and **Pinecone**. This application acts as an intelligent HR and company policy assistant, featuring simulated Single Sign-On (SSO) with Role-Based Access Control (RBAC), and agentic tool use.

## Features

- **Simulated SSO & RBAC:** Switch between `Employee` and `HR` roles to experience tailored UI access. Only HR personnel can access the Knowledge Base Management section to upload new policies.
- **Hybrid Search (Dense + Sparse):** Uses Pinecone's `dotproduct` metric to combine OpenAI dense semantic embeddings with a custom pure-Python BM25 sparse encoder, ensuring highly accurate retrieval for both conceptual queries and exact keyword matches (like policy IDs).
- **Agentic Assistant:** Built with LangGraph, the AI assistant dynamically decides when to use tools:
  - `get_my_employment_records`: Fetches secure employee information from a local SQLite database based on the currently logged-in user.
  - `search_company_policies`: Uses Pinecone Vector DB to retrieve company policy documents via Hybrid Search.
- **Automated Citations:** The assistant provides clickable markdown citations linking directly to the source policy documents it references.
- **Feedback Loop:** Users can thumbs-up or thumbs-down AI responses. Corrections are saved to a local SQLite database and injected into the system prompt to prevent the agent from repeating mistakes.
- **High Resiliency:** The LLM is configured with fallback mechanisms to ensure high availability.

## Prerequisites

- Python 3.9+
- Pinecone Account (Free tier works)
- OpenAI API Key

## Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd "agentic rag"
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Mac/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install rank-bm25 # Used for the custom sparse encoder
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add your API keys:
   ```env
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX_NAME=company-policies
   OPENAI_API_KEY=your_openai_api_key
   ```

5. **Initialize Database:**
   Seed the SQLite database with mock employee data:
   ```bash
   python database.py
   ```

## Usage

1. **Run the Streamlit application:**
   ```bash
   streamlit run ui/app.py
   ```

2. **Interact:**
   - Use the sidebar to simulate logging in as an Employee or HR.
   - If logged in as HR, you can upload `.pdf` documents to be ingested into Pinecone.
   - Chat with the Enterprise AI Assistant to query employment records or ask about company policies.

## Architecture

* **UI:** Streamlit
* **Agent Framework:** LangGraph / LangChain Core
* **Vector Database:** Pinecone (using `dotproduct` metric for hybrid search)
* **Embeddings:** OpenAI `text-embedding-3-small` (Dense) + Custom `rank-bm25` Encoder (Sparse)
* **LLM:** OpenAI `gpt-4o-mini` (with fallback to Google Gemini `gemini-1.5-flash`)
* **Relational DB:** SQLite (for employee records and feedback logs)
