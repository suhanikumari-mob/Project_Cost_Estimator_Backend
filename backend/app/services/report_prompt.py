from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate

# prompt_text = Path(
#     "app/prompts/pdf_prompt.txt"
# ).read_text(encoding="utf-8")

# prompt = ChatPromptTemplate.from_template(prompt_text)

# prompt_text_xls = Path(
#     "app/prompts/excel_prompt.txt"
# ).read_text(encoding="utf-8")

# prompt_xls = ChatPromptTemplate.from_template(prompt_text_xls)


prompt_text_json = Path(
    "app/prompts/json_prompt.txt"
).read_text(encoding="utf-8")

json_prompt = ChatPromptTemplate.from_template(prompt_text_json)


prompt_text_quest = Path(
    "app/prompts/quest_prompt.txt"
).read_text(encoding="utf-8")

quest_prompt = ChatPromptTemplate.from_template(prompt_text_quest)