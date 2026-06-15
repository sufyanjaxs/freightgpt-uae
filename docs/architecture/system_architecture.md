# FreightGPT UAE - System Architecture

## Overview

FreightGPT UAE is a multi-agent AI system designed to autonomously operate freight logistics in the GCC region. Each agent specializes in a specific domain and collaborates through a central orchestrator.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Clients                              │
│  Web App (Next.js)  │  Mobile App (React Native)  │  API   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (FastAPI)                     │
│  Auth │ RBAC │ Rate Limiting │ Audit Logging │ Caching      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent Orchestrator                        │
│  LangGraph Workflows │ CrewAI Teams │ Task Queue (Celery)   │
└────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬───────┘
     │      │      │      │      │      │      │      │
     ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼
┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐
│MI │ │LA │ │SA │ │SA │ │DA │ │DC │ │PA │ │DAI│ │FA │ │CA │
└───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘
     │      │      │      │      │      │      │      │
     └──────┴──────┴──────┴──────┴──────┴──────┴──────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                     LLM Router                               │
│  GPT-4 │ Claude 3 │ Ollama │ DeepSeek │ (Model Fallback)    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌──────────┐ ┌──────┐ ┌──────┐ ┌──────────┐ ┌───────────────┐
│PostgreSQL│ │Redis │ │Qdrant│ │  Object  │ │    Search     │
│ (Primary)│ │(Cache)│ │(Vectors)│ │ Storage │ │   (Elastic)   │
└──────────┘ └──────┘ └──────┘ └──────────┘ └───────────────┘
```

## Agent Communication Flow

1. **User Request** comes through API Gateway
2. **Agent Orchestrator** routes to appropriate agent(s)
3. Each agent uses **LLM Router** for AI inference
4. Agents read/write to **PostgreSQL** for persistence
5. **Redis** handles caching, real-time updates, and pub/sub
6. **Qdrant** stores document embeddings for semantic search
7. **Celery** handles async/background tasks

## Data Flow: Load Acquisition

```
Load Board → Market Intelligence Agent (detects new load)
    → Pricing Agent (calculates optimal rate)
    → Load Acquisition Agent (prepares bid)
    → Approval Request → Dispatch Agent (assigns truck/driver)
    → Route Planning → Driver Copilot (navigates)
    → Document AI (processes POD)
    → Finance Agent (generates invoice)
    → CEO Agent (reports)
```

## Security Architecture

- **Authentication:** JWT with access/refresh tokens
- **Authorization:** Role-Based Access Control (RBAC)
- **Tenancy:** Multi-tenant data isolation at DB level
- **Audit:** All operations logged with user, action, resource
- **Encryption:** TLS for transit, AES for sensitive data at rest
- **API Security:** Rate limiting, CORS, input validation

## Scaling Strategy

- **Horizontal scaling** via Kubernetes HPA (CPU/Memory based)
- **Database read replicas** for analytics queries
- **Redis cluster** for distributed caching
- **Celery worker pools** for async agent tasks
- **CDN** for static assets and document storage
- **Connection pooling** with PgBouncer for PostgreSQL
