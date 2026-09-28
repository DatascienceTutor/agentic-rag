from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

class TestModel(BaseModel):
    name: str

primary = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key="fake")
fallback = ChatOpenAI(model="gpt-4o-mini", openai_api_key="fake")

# Create a resilient LLM
resilient = primary.with_fallbacks([fallback])

# Apply structured output
try:
    s_llm = resilient.with_structured_output(TestModel)
    prompt = PromptTemplate.from_template("What is {query}")
    chain = prompt | s_llm
    
    # This should fail because both API keys are fake, but it will let us see if fallback was attempted
    chain.invoke({"query": "your name?"})
except Exception as e:
    import traceback
    traceback.print_exc()
