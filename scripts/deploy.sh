#!/bin/bash
set -e

echo "🚀 FreightGPT UAE Deployment Script"
echo "===================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check prerequisites
check_prereqs() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker is required${NC}"; exit 1; }
    command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}kubectl is required${NC}"; exit 1; }
    command -v helm >/dev/null 2>&1 || { echo -e "${YELLOW}Helm not found, skipping Helm charts${NC}"; }
    
    echo -e "${GREEN}✓ Prerequisites met${NC}"
}

# Build and push Docker images
build_images() {
    echo -e "${YELLOW}Building Docker images...${NC}"
    
    docker build -t freightgpt/backend:latest -f infra/docker/Dockerfile.backend .
    docker build -t freightgpt/frontend:latest -f infra/docker/Dockerfile.frontend .
    docker build -t freightgpt/celery-worker:latest -f infra/docker/Dockerfile.celery .
    
    echo -e "${GREEN}✓ Images built${NC}"
}

# Deploy to Kubernetes
deploy_k8s() {
    local env=$1
    echo -e "${YELLOW}Deploying to ${env} environment...${NC}"
    
    kubectl apply -k infra/k8s/overlays/${env}/
    
    echo -e "${GREEN}✓ Deployed to ${env}${NC}"
}

# Run database migrations
run_migrations() {
    echo -e "${YELLOW}Running database migrations...${NC}"
    
    kubectl exec -n freightgpt deployment/backend -- alembic upgrade head
    
    echo -e "${GREEN}✓ Migrations complete${NC}"
}

# Main deployment flow
main() {
    local env=${1:-dev}
    
    check_prereqs
    build_images
    
    if [ "$env" == "k8s" ]; then
        deploy_k8s "${2:-dev}"
        run_migrations
    else
        echo -e "${YELLOW}Starting local development environment...${NC}"
        docker compose -f infra/docker/docker-compose.yml up -d
        echo -e "${GREEN}✓ Local environment started${NC}"
    fi
    
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}✅ FreightGPT UAE deployment complete!${NC}"
    echo -e "${GREEN}================================${NC}"
}

main "$@"
