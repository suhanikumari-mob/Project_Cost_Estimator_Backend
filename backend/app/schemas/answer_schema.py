from pydantic import BaseModel
from typing import List

class AnswerItem(BaseModel):
    id: int
    question: str
    answer: str

class AnswerRequest(BaseModel):
    answers: List[AnswerItem]