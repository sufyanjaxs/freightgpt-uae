.PHONY: install run run-backend run-frontend setup clean help

help: ## Show this help
	@echo "FreightGPT UAE - Quick Start"
	@echo "============================"
	@echo "  make install     - Install all dependencies"
	@echo "  make run         - Run backend + frontend together"
	@echo "  make run-backend - Run backend only (FastAPI)"
	@echo "  make run-frontend- Run frontend only (Next.js)"
	@echo "  make setup       - Full setup + install Ollama models"
	@echo "  make clean       - Clean all caches"
	@echo ""
	@echo "PREREQUISITES:"
	@echo "  Python 3.11+   (https://python.org)"
	@echo "  Node.js 20+    (https://nodejs.org)"
	@echo "  Ollama (opt)   (https://ollama.ai) - for AI features"
	@echo ""
	@echo "QUICK START (no Ollama needed):"
	@echo "  make install && make run"

install: ## Install all dependencies
	@echo "Installing Python dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing Node dependencies..."
	cd frontend && npm install
	@echo "Creating uploads directory..."
	mkdir -p backend/uploads
	@echo "✅ All dependencies installed!"

run: run-backend run-frontend ## Run full stack

run-backend: ## Start the FastAPI backend
	@echo "🚀 Starting FreightGPT backend on http://localhost:8000"
	@echo "📚 API Docs: http://localhost:8000/docs"
	cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Start the Next.js frontend
	@echo "🚀 Starting FreightGPT frontend on http://localhost:3000"
	cd frontend && npm run dev

setup: ## Full setup with Ollama
	pip install -r backend/requirements.txt
	cd frontend && npm install || true
	@echo "Checking Ollama..."
	ollama pull mistral 2>/dev/null || echo "Ollama not found. Install from https://ollama.ai"
	ollama pull phi 2>/dev/null || true
	@echo "✅ Setup complete! Run 'make run'"

test: ## Run tests
	cd backend && python -m pytest tests/ -v

clean: ## Clean temporary files
	rm -rf backend/__pycache__ backend/**/__pycache__
	rm -rf frontend/.next frontend/node_modules
	rm -rf backend/*.db
	@echo "✅ Cleaned!"
