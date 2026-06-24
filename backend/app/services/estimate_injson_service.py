from langchain_core.prompts import ChatPromptTemplate
from app.services.report_prompt import json_prompt
from .llm import llm
import regex as re





# def estimator_json(docs,answer) -> str:
#     """Returns a json."""
#     chain = json_prompt | llm
#     response = chain.invoke({"docs": docs,"answer":answer})
#     return response.content if isinstance(response.content, str) else response.content[0]["text"]


# estimate_injson_service.py
def estimator_json(docs, answer) -> str:
    chain = json_prompt | llm
    response = chain.invoke({"docs": docs, "answer": answer})
    
    # Extract content
    if isinstance(response.content, str):
        content = response.content
    elif isinstance(response.content, list):
        content = response.content[0].get("text", "")
    else:
        content = ""
    
    print(f"RAW LLM RESPONSE: {repr(content[:500])}")  # debug — see what's coming back
    
    # Strip markdown fences if present
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```[a-zA-Z]*\n?", "", content)
        content = re.sub(r"```$", "", content.strip())
    
    if not content:
        raise ValueError("LLM returned empty response")
    
    return content