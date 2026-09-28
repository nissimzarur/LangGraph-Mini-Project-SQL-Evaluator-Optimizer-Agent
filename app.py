import gradio as gr

from graph import graph


DEFAULT_SCHEMA = """users(
    id INTEGER,
    name TEXT,
    email TEXT,
    created_at TIMESTAMP
)

orders(
    id INTEGER,
    user_id INTEGER,
    total DECIMAL,
    status TEXT,
    created_at TIMESTAMP
)"""


DEFAULT_REQUEST = (
    "Return the top 5 users by total revenue from paid orders."
)


def run_agent(schema: str, request: str):
    if not schema.strip():
        return "", "Schema is required.", ""

    if not request.strip():
        return "", "Request is required.", ""

    initial_state = {
        "schema": schema,
        "request": request,
        "sql": "",
        "score": 0,
        "issues": [],
        "feedback": "",
        "attempts": 0,
        "history": [],
    }

    result = graph.invoke(initial_state)

    status = (
        f"Final score: {result['score']}/10 | "
        f"Attempts: {result['attempts']}"
    )

    trace = "\n\n---\n\n".join(result["history"])

    return result["sql"], status, trace


with gr.Blocks(title="LangGraph SQL Evaluator") as demo:
    gr.Markdown(
        """
# SQL Evaluator–Optimizer

Generate SQL, evaluate it, and automatically retry when quality is too low.

**Pattern:** Generate → Evaluate → Route → Retry / End
"""
    )

    schema_input = gr.Textbox(
        label="Database Schema",
        value=DEFAULT_SCHEMA,
        lines=12,
    )

    request_input = gr.Textbox(
        label="SQL Request",
        value=DEFAULT_REQUEST,
        lines=3,
    )

    run_button = gr.Button("Run Agent")

    final_sql = gr.Code(
        label="Final SQL",
        language="sql",
    )

    status = gr.Textbox(
        label="Result",
        interactive=False,
    )

    trace = gr.Markdown()

    run_button.click(
        fn=run_agent,
        inputs=[schema_input, request_input],
        outputs=[final_sql, status, trace],
    )


if __name__ == "__main__":
    demo.launch()
