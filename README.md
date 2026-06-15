# FreightGPT UAE

**Autonomous Logistics OS - 100% Free & Open-Source**

Zero paid services required. Runs on SQLite (no DB server), Ollama (local LLM), and OpenStreetMap (free maps).

## Quick Start (30 seconds)

```bash
# 1. Install Python deps
cd backend
pip install -r requirements.txt

# 2. Start the API
python -m uvicorn main:app --reload --port 8000

# 3. Open in browser
#    API: http://localhost:8000/docs
#    Setup check: http://localhost:8000/setup
```

## For AI Features (Optional)

Install [Ollama](https://ollama.ai) for free local AI:

```bash
ollama pull mistral
# That's it! AI agents will now use Mistral for free
```

## Free vs Paid Architecture

| Service | Free Default | Paid Alternative |
|---------|-------------|------------------|
| **LLM** | Ollama (Mistral, Phi, Llama) | OpenAI GPT-4 |
| **Database** | SQLite (zero config) | PostgreSQL |
| **Maps** | OpenStreetMap + OSRM | Google Maps |
| **Email** | Gmail SMTP | SendGrid |
| **Storage** | Local filesystem | AWS S3 |
| **Voice/SMS** | Console logging | Twilio |
| **Vector DB** | In-memory | Qdrant |

## Project Structure

```
freightgpt-uae/
├── backend/
│   ├── agents/          # 10 AI Agents
│   ├── api/v1/          # REST API endpoints
│   ├── core/            # Config, DB, LLM router
│   ├── db/models/       # SQLAlchemy models (SQLite+Postgres)
│   ├── integrations/    # Email, Maps, Storage
│   └── tests/           # Pytest suite
├── frontend/            # Next.js dashboard (optional)
├── .devcontainer/       # GitHub Codespaces config
└── Makefile             # Quick commands
```

## API Endpoints

Check `http://localhost:8000/docs` for full Swagger documentation.

Key endpoints:
- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/auth/login` - Sign in
- `GET /api/v1/loads` - List freight loads
- `POST /api/v1/agents/run` - Run any AI agent
- `GET /api/v1/analytics/dashboard` - Business metrics
- `GET /api/v1/setup` - System health check

## Deploy to GitHub

```bash
git init
git add .
git commit -m "Initial commit: FreightGPT UAE"
git remote add origin https://github.com/YOUR_USER/freightgpt-uae.git
git push -u origin main
```

Then open in **GitHub Codespaces** for instant development environment.
