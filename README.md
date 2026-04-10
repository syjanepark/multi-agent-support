# Multi-Agent Customer Support

A LangGraph-based multi-agent system that routes customer support queries to specialized agents backed by Azure OpenAI and Azure AI Search (RAG).

## Architecture

```
Customer Query
      │
   [Triage]
      │
      ├──► [Billing]   ──┐
      ├──► [Technical] ──┼──► [Synthesize] ──► Response
      ├──► [Account]   ──┤
      ├──► [General]   ──┘
      │
      └──► [Escalation] ──► Human handoff
```

**Triage** classifies the query and routes to one of four specialized agents. Each agent queries the RAG tool against a domain-specific knowledge base, then either synthesizes a response or escalates to a human agent. Escalation is also triggered directly from triage when confidence is low.

### Agents

| Agent | Escalates when |
|---|---|
| `BillingAgent` | Refund/transaction amount > $500 |
| `TechnicalAgent` | Outage or service-down keywords detected |
| `AccountAgent` | Security incident keywords (breach, hacked, locked out) |
| `GeneralAgent` | FAQ / catch-all; passes through validation |
| `ResponseSynthesizer` | — rewrites agent output into customer-facing prose |

## Project Structure

```
agents/
  base.py              # BaseAgent with RAG + LLM call logic
  triage.py            # TriageAgent — classifies and routes queries
  billing.py           # BillingAgent — billing and refund queries
  technical.py         # TechnicalAgent — technical support queries
  account.py           # AccountAgent — account management queries
  general.py           # GeneralAgent — FAQ / catch-all
  synthesizer.py       # ResponseSynthesizer — rewrites agent output

graph/
  state.py             # GraphState TypedDict + shared Pydantic models
  nodes.py             # LangGraph node functions wrapping each agent
  edges.py             # Conditional routing logic
  orchestrator.py      # StateGraph assembly and compilation

api/
  main.py              # FastAPI app (CORS, lifespan, endpoint handlers)
  schemas.py           # Pydantic request/response models

dashboard/             # Next.js monitoring dashboard (port 3000)
  app/                 # Next.js App Router pages
  components/          # UI components (charts, metrics cards, query tester)
  hooks/
    use-dashboard-data.ts  # SWR hooks for /health and /metrics; submitQuery
  lib/
    types.ts           # TypeScript types mirroring API schemas

monitoring/
  logger.py            # structlog configuration
  metrics_collector.py # In-memory metrics collector (thread-safe)

evaluation/
  evaluator.py         # SystemEvaluator — calls API, scores with LLM judge
  run_eval.py          # Entry point: python -m evaluation.run_eval
  ground_truth.json    # Labeled test cases with expected_agent + required_topics

config/
  settings.py          # Pydantic settings (Azure credentials, thresholds)
  prompts.py           # Prompt templates for each agent

tools/
  rag_tool.py          # Azure AI Search retrieval tool
  calculator_tool.py   # Billing calculation tool
  index_builder.py     # Script to build the Azure Search index

data/
  knowledge_base/      # billing_policies.md, technical_docs.md, account_docs.md, general_faq.md

tests/
  test_triage.py
  test_agents.py       # Per-agent smoke tests with escalation assertions
  test_e2e.py          # End-to-end graph tests
  test_rag.py
  test_azure.py
```

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in Azure credentials
```

### Required environment variables

```
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-5-mini
AZURE_OPENAI_MINI_DEPLOYMENT=gpt-5-nano
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small

AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_KEY=
AZURE_SEARCH_INDEX=customer-support-index
```

## Running

### API

```bash
uvicorn api.main:app --reload
# → http://localhost:8000
```

### Dashboard

```bash
cd dashboard
npm install
npm run dev
# → http://localhost:3000
```

Set `NEXT_PUBLIC_API_URL` in `dashboard/.env.local` if the backend runs on a different host/port (defaults to `http://localhost:8000`).

### Evaluation

```bash
# Requires the API to be running
python -m evaluation.run_eval
# Results are reflected in the dashboard metrics
```

### Tests

```bash
# Smoke-test individual agents
python tests/test_agents.py

# Full end-to-end graph test
python tests/test_e2e.py

# Run pytest suite
pytest tests/
```

## API Reference

Base URL: `http://localhost:8000`

---

### `POST /support`

Process a customer support query through the multi-agent graph.

**Request**
```json
{
  "query": "Why was I charged twice this month?",
  "customer_id": "cust_123",   // optional
  "session_id": "sess_abc"     // optional — used as LangGraph thread_id for state persistence
}
```

**Response**
```json
{
  "response": "We found a duplicate charge on...",
  "agent_used": "billing",
  "confidence": 0.92,
  "routing_confidence": 0.88,
  "sources": ["billing_policies.md#section-3"],
  "suggested_followups": ["How do I request a refund?"],
  "was_escalated": false,
  "response_time": 1.243,
  "cost": 0.000412
}
```

| Field | Description |
|---|---|
| `agent_used` | Which specialized agent handled the query |
| `confidence` | Agent's confidence in its response (0–1) |
| `routing_confidence` | Triage confidence in its routing decision (0–1) |
| `was_escalated` | `true` if routed to human handoff |
| `cost` | Estimated OpenAI token cost in USD |

---

### `GET /health`

Returns API status and uptime.

**Response**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "agents": ["triage", "billing", "technical", "account", "general"],
  "uptime_seconds": 3612.4
}
```

---

### `GET /metrics`

Returns aggregated metrics across all processed queries (in-memory, resets on restart).

**Response**
```json
{
  "total_queries": 42,
  "avg_response_time": 1.832,
  "avg_cost": 0.000387,
  "escalation_rate": 0.071,
  "agent_distribution": { "billing": 18, "technical": 12, "account": 7, "general": 5 },
  "agent_performance": {
    "billing": {
      "accuracy": 0.87,
      "avg_relevance": 0.87,
      "avg_response_time": 1.94,
      "total_cases": 18
    }
  },
  "latency_histogram": [1.2, 0.9, 2.1, ...],
  "cost_over_time": [
    { "timestamp": "2026-03-10T14:22:01.123456", "cumulative_cost": 0.000412 }
  ]
}
```

---

## Configuration

Key thresholds in `config/settings.py`:

| Setting | Default | Effect |
|---|---|---|
| `routing_confidence_threshold` | `0.7` | Minimum triage confidence before escalating |
| `escalation_confidence_threshold` | `0.5` | Agent confidence below this triggers human handoff |
| `max_turns` | `5` | Max conversation turns |
| `max_cost_per_query` | `$0.10` | Cost ceiling per request |
