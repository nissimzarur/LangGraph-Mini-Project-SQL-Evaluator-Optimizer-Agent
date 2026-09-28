from typing_extensions import TypedDict
from pydantic import BaseModel, Field


class Evaluation(BaseModel):
    score: int = Field(ge=0, le=10)
    issues: list[str]
    feedback: str


class AgentState(TypedDict):
    schema: str
    request: str

    sql: str

    score: int
    issues: list[str]
    feedback: str

    attempts: int
    history: list[str]
