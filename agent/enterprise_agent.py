from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

from core.config import PINECONE_INDEX_NAME, PINECONE_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY
from core.llm_factory import get_resilient_llm
from db.database import get_employee_record_secure
from agent.guardrails import validate_user_input
from db.feedback_store import get_learned_corrections

def search_company_policies_tool(query: str) -> str:
    """Searches the company policies knowledge base using Hybrid Search (Dense + Sparse)."""
    import os
    from pinecone import Pinecone
    from rag.custom_bm25 import CustomBM25Encoder
    
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small", 
        openai_api_key=OPENAI_API_KEY
    )
    
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
    
    # Generate Dense Vector
    dense_vec = embeddings.embed_query(query)
    
    # Generate Sparse Vector
    bm25 = CustomBM25Encoder()
    bm25_path = "bm25_encoder.json"
    if os.path.exists(bm25_path):
        bm25.load(bm25_path)
    sparse_vec = bm25.encode_queries(query)
    
    # Query Pinecone using both vectors (alpha weighting can be done manually or Pinecone handles sparse/dense natively)
    # Pinecone natively combines them when both are provided
    response = index.query(
        vector=dense_vec,
        sparse_vector=sparse_vec,
        top_k=5,
        include_metadata=True
    )
    
    docs = response.matches
    
    if not docs:
        return "No relevant company policies found."
    
    formatted_docs = []
    for doc in docs:
        source = doc.metadata.get("source", "Unknown Document")
        # Ensure we fetch text which might be in metadata depending on ingestion
        # Wait, our new ingest script puts 'source' in metadata but doesn't explicitly put 'text' in metadata!
        # Langchain puts page_content in 'text' key inside metadata by default. Let's extract it.
        content = doc.metadata.get("text", doc.metadata.get("page_content", ""))
        formatted_docs.append(f"Source: {source}\nContent: {content}")
        
    return "\n\n---\n\n".join(formatted_docs)


def build_session_agent(auth_emp_code: str, auth_emp_name: str):
    """
    Builds the agent orchestrator bound to a specific authenticated user.
    """
    llm = get_resilient_llm(temperature=0.0)
    
    @tool
    def get_my_employment_records() -> str:
        """Retrieves your personal employment records. This tool takes no arguments."""
        record = get_employee_record_secure(auth_emp_code)
        if not record:
            return "No employment record found."
        return str(record)
    
    @tool
    def search_company_policies(query: str) -> str:
        """Searches the company policies knowledge base for relevant documents."""
        return search_company_policies_tool(query)

    tools = [get_my_employment_records, search_company_policies]
    
    # Inject learned corrections into the system prompt
    corrections = get_learned_corrections(limit=5)
    corrections_text = "None"
    if corrections:
        corrections_text = "\n".join([f"- User asked: '{c['query']}'. Correction learned: {c['notes']}" for c in corrections])
    
    system_prompt = f"""You are the Enterprise Agentic RAG assistant. 
You are currently assisting employee: {auth_emp_name} (Code: {auth_emp_code}).

You have access to two tools:
1. get_my_employment_records: Use this to fetch the user's personal employment information.
2. search_company_policies: Use this to search the vector database for company policies and guidelines.

Always use these tools to gather information before answering. Do not guess or hallucinate information.

IMPORTANT CITATION INSTRUCTION:
When you use information from a company policy provided by the search_company_policies tool, you MUST include a clickable citation to the document in your response. 
Format the citation as a markdown link using the "Source" filename provided by the tool, like this: `[Document Name](data/Document_Filename.pdf)` (e.g. `[Remote Work Policy](data/POL-HR-001_Remote_Work_Policy.pdf)`).

Previous user feedback and learned corrections to incorporate in your behavior:
{corrections_text}
"""
    
    agent = create_react_agent(llm, tools, prompt=system_prompt)
    return agent


def run_enterprise_pipeline(user_query: str, emp_code: str, emp_name: str):
    """
    Main entry point for handling user queries. Implements security guardrails and routes to the agent.
    Yields chunks for streaming.
    """
    # 1. Apply Security Guardrails
    validation = validate_user_input(user_query)
    if not validation.is_safe:
        yield f"Request blocked by security guardrails. Reason: {validation.reason}"
        return
        
    # 2. Build and run agent with user context
    agent_executor = build_session_agent(emp_code, emp_name)
    
    try:
        # 3. Stream the output back
        for msg, metadata in agent_executor.stream({"messages": [("user", user_query)]}, stream_mode="messages"):
            msg_type = getattr(msg, "type", "")
            if msg_type in ("ai", "AIMessageChunk") and msg.content:
                if isinstance(msg.content, str):
                    yield msg.content
                elif isinstance(msg.content, list):
                    for block in msg.content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            yield block["text"]
    except Exception as e:
        yield f"\n\n**Error:** The LLM encountered an issue (likely a rate limit). Details: {str(e)}"
