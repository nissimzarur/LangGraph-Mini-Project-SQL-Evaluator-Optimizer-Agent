# SQL Evaluator–Optimizer Agent

A LangGraph-based agent that generates SQL queries, evaluates them against a quality rubric, and automatically retries until the result meets a score threshold.

**Pattern:** Generate → Evaluate → Route → Retry / End

## How It Works

1. **Generate** — An LLM produces a SQL query based on the database schema and user request.
2. **Evaluate** — A second LLM call scores the query (0–10) on correctness, schema adherence, efficiency, and clarity.
3. **Route** — If the score is below 8, the agent retries with feedback from the evaluator (up to 3 attempts).

## Project Structure

```
app.py      — Gradio UI
graph.py    — LangGraph state graph (generate → evaluate → route)
models.py   — Pydantic models and agent state definition
```

## Setup

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install langchain-ollama langgraph gradio python-dotenv

# Make sure Ollama is running with the qwen3:14b model
ollama pull qwen3:14b

# Configure the model (optional — defaults to qwen3:14b)
echo "OLLAMA_MODEL=qwen3:14b" > .env
```

## Usage

```bash
python app.py
```

This launches a Gradio interface where you can:
- Enter a database schema
- Describe the SQL query you need
- Watch the agent generate, evaluate, and refine the query

## Configuration

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_MODEL` | `qwen3:14b` | Ollama model used for generation and evaluation (via `.env`) |
| `MAX_ATTEMPTS` | `3` | Maximum retry attempts |
| `PASS_SCORE` | `8` | Minimum score to accept a query |
