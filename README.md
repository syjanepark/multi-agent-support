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
agents/          # Specialized agent implementations + base class
graph/
  state.py       # GraphState TypedDict, shared Pydantic models
  nodes.py       # LangGraph node functions wrapping each agent
  edges.py       # Conditional routing functions
  orchestrator.py# StateGraph assembly and compilation
config/
  settings.py    # Pydantic settings (Azure keys, thresholds)
  prompts.py     # Prompt templates
tools/
  rag_tool.py    # Azure AI Search retrieval
  calculator_tool.py
  index_builder.py
monitoring/      # structlog logger, cost tracker, metrics collector
evaluation/      # Evaluator and metrics
data/
  knowledge_base/ # billing_policies.md, technical_docs.md, account_docs.md, general_faq.md
api/             # FastAPI app (main.py, schemas.py)
dashboard/       # Monitoring dashboard
tests/
  test_triage.py
  test_agents.py  # Per-agent smoke tests with escalation assertions
  test_e2e.py     # End-to-end graph tests
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

```bash
# Smoke-test individual agents
python tests/test_agents.py

# Full end-to-end graph test
python tests/test_e2e.py

# Run pytest suite
pytest tests/
```

## Configuration

Key thresholds in `config/settings.py`:

| Setting | Default | Effect |
|---|---|---|
| `routing_confidence_threshold` | `0.7` | Minimum triage confidence before escalating |
| `escalation_confidence_threshold` | `0.5` | Agent confidence below this triggers human handoff |
| `max_turns` | `5` | Max conversation turns |
| `max_cost_per_query` | `$0.10` | Cost ceiling per request |
