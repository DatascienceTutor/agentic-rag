from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from core.config import GOOGLE_API_KEY, OPENAI_API_KEY

def get_resilient_llm(temperature=0.0):
    """
    Returns a resilient LLM setup with OpenAI GPT-4o-mini as primary, 
    falling back to Google Gemini if it fails.
    """
    primary_llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=temperature,
        openai_api_key=OPENAI_API_KEY
    )
    
    fallback_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=temperature,
        google_api_key=GOOGLE_API_KEY
    )
    
    # Configure fallback behavior
    resilient_llm = primary_llm.with_fallbacks([fallback_llm])
    
    return resilient_llm
