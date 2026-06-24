# from langchain_core.prompts import ChatPromptTemplate
from app.services.report_prompt import quest_prompt
from .llm import llm
import json





def question_generator(docs,query) -> str:
    """Returns a json."""
    chain = quest_prompt | llm
    response = chain.invoke({"docs": docs,"query": query})
    # data = response.content if isinstance(response.content, str) else response.content[0]["text"]
    # data = json.loads(response.content)
    content = response.content

    if isinstance(content, str):
        return json.loads(content)

    if isinstance(content, list):
        text = content[0]["text"]
        return json.loads(text)

    raise ValueError(f"Unexpected content type: {type(content)}")
    # return data

