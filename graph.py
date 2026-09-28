from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph

from models import AgentState, Evaluation


MODEL = "qwen3:14b"

MAX_ATTEMPTS = 3
PASS_SCORE = 8

llm = ChatOllama(model=MODEL)
evaluator_llm = llm.with_structured_output(Evaluation)


def generate_sql(state: AgentState) -> dict:
    attempt = state.get("attempts", 0) + 1
    previous_feedback = state.get("feedback", "")

    prompt = f"""
You are a senior SQL engineer.

Generate a SQL query that satisfies the user's request.

DATABASE SCHEMA:
{state["schema"]}

USER REQUEST:
{state["request"]}

FEEDBACK FROM THE PREVIOUS ATTEMPT:
{previous_feedback or "No previous feedback. This is the first attempt."}

Rules:
- Use only tables and columns from the provided schema.
- Do not invent fields.
- Prefer clear and reasonably efficient SQL.
- Return only the SQL query.
- Do not wrap the query in Markdown.
"""

    response = llm.invoke(prompt)
    sql = str(response.content).strip()

    history = state.get("history", []).copy()
    history.append(
        f"""### Attempt {attempt} — Generated SQL

{sql}"""
    )

    return {
        "sql": sql,
        "attempts": attempt,
        "history": history,
    }


def evaluate_sql(state: AgentState) -> dict:
    prompt = f"""
You are reviewing a SQL query.

DATABASE SCHEMA:
{state["schema"]}

USER REQUEST:
{state["request"]}

SQL QUERY:
{state["sql"]}

Evaluate the query using this rubric:

1. Correctness: 0-4 points
2. Schema adherence: 0-2 points
3. Efficiency: 0-2 points
4. Clarity and safety: 0-2 points

Return:
- score from 0 to 10
- concrete issues
- short feedback explaining what should be changed
"""

    evaluation = evaluator_llm.invoke(prompt)

    history = state.get("history", []).copy()

    issues_text = (
        "\n".join(f"- {issue}" for issue in evaluation.issues)
        if evaluation.issues
        else "- No significant issues"
    )

    history.append(
        f"""### Attempt {state["attempts"]} — Evaluation

Score: {evaluation.score}/10

Issues:
{issues_text}

Feedback:
{evaluation.feedback}"""
    )

    return {
        "score": evaluation.score,
        "issues": evaluation.issues,
        "feedback": evaluation.feedback,
        "history": history,
    }


def route_after_evaluation(state: AgentState) -> str:
    if state["score"] >= PASS_SCORE:
        return "done"

    if state["attempts"] >= MAX_ATTEMPTS:
        return "done"

    return "retry"


builder = StateGraph(AgentState)

builder.add_node("generate", generate_sql)
builder.add_node("evaluate", evaluate_sql)

builder.add_edge(START, "generate")
builder.add_edge("generate", "evaluate")

builder.add_conditional_edges(
    "evaluate",
    route_after_evaluation,
    {
        "retry": "generate",
        "done": END,
    },
)

graph = builder.compile()
