#!/bin/bash
# Development environment startup script for Crypto Sentinel Bot

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

SERVICE="${1:-all}"
LOGS=false
BUILD=false
CLEAN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --logs) LOGS=true; shift ;;
        --build) BUILD=true; shift ;;
        --clean) CLEAN=true; shift ;;
        api|bot|dashboard|all) SERVICE=$1; shift ;;
        *) shift ;;
    esac
done

echo -e "\033[36m🚀 Crypto Sentinel Bot - Development Environment\033[0m"
echo -e "\033[36m================================================\033[0m"

# Check if .env exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "\033[33m⚠️  .env file not found. Creating from .env.example...\033[0m"
        cp .env.example .env
        echo -e "\033[33m📝 Please edit .env with your actual values\033[0m"
    else
        echo -e "\033[31m❌ No .env or .env.example found!\033[0m"
        exit 1
    fi
fi

# Clean if requested
if [ "$CLEAN" = true ]; then
    echo -e "\033[33m🧹 Cleaning up containers and volumes...\033[0m"
    docker-compose down -v --remove-orphans
fi

# Build if requested
if [ "$BUILD" = true ]; then
    echo -e "\033[34m🔨 Building Docker images...\033[0m"
    docker-compose build --no-cache
fi

start_all_services() {
    echo -e "\033[32m🐳 Starting all services with Docker Compose...\033[0m"
    docker-compose up -d
    
    echo -e "\n\033[32m✅ Services started!\033[0m"
    echo -e "\n\033[36m📊 Service URLs:\033[0m"
    echo "   - Dashboard: http://localhost:3000"
    echo "   - API:       http://localhost:8080"
    echo "   - API Docs:  http://localhost:8080/docs"
    echo "   - MongoDB:   mongodb://localhost:27017"
    echo "   - Redis:     redis://localhost:6379"
}

start_api_only() {
    echo -e "\033[32m🔌 Starting API service...\033[0m"
    docker-compose up -d mongodb redis api
    echo -e "\n\033[32m✅ API started at http://localhost:8080\033[0m"
}

start_bot_only() {
    echo -e "\033[32m🤖 Starting Bot service...\033[0m"
    docker-compose up -d mongodb redis bot
    echo -e "\n\033[32m✅ Bot started!\033[0m"
}

start_dashboard_only() {
    echo -e "\033[32m📊 Starting Dashboard service...\033[0m"
    
    if [ ! -d "dashboard" ]; then
        echo -e "\033[31m❌ Dashboard directory not found!\033[0m"
        exit 1
    fi
    
    # Start dependencies first
    docker-compose up -d mongodb redis api
    
    # Start dashboard with hot reload
    cd dashboard
    
    if [ ! -d "node_modules" ]; then
        echo -e "\033[33m📦 Installing dashboard dependencies...\033[0m"
        npm install
    fi
    
    echo -e "\033[32m🔄 Starting dashboard with hot reload...\033[0m"
    npm run dev
}

# Start services based on selection
case $SERVICE in
    api) start_api_only ;;
    bot) start_bot_only ;;
    dashboard) start_dashboard_only ;;
    all) start_all_services ;;
esac

# Show logs if requested
if [ "$LOGS" = true ] && [ "$SERVICE" != "dashboard" ]; then
    echo -e "\n\033[36m📋 Showing logs (Ctrl+C to exit)...\033[0m"
    
    case $SERVICE in
        api) docker-compose logs -f api ;;
        bot) docker-compose logs -f bot ;;
        all) docker-compose logs -f ;;
    esac
fi

echo -e "\n\033[33m💡 Useful commands:\033[0m"
echo "   docker-compose logs -f          # View all logs"
echo "   docker-compose logs -f api      # View API logs"
echo "   docker-compose ps               # List running services"
echo "   docker-compose down             # Stop all services"
