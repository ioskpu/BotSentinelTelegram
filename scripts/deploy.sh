#!/bin/bash
# Deployment script for Crypto Sentinel Bot

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

PLATFORM="${1:-docker}"
SERVICE="${2:-all}"
ENVIRONMENT="${3:-staging}"
TAG="latest"
DRY_RUN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true; shift ;;
        --tag) TAG="$2"; shift 2 ;;
        --env) ENVIRONMENT="$2"; shift 2 ;;
        fly|railway|docker|docker-prod) PLATFORM=$1; shift ;;
        api|dashboard|bot|all) SERVICE=$1; shift ;;
        staging|production) ENVIRONMENT=$1; shift ;;
        *) shift ;;
    esac
done

echo -e "\033[36m🚀 Crypto Sentinel Bot - Deployment\033[0m"
echo -e "\033[36m====================================\033[0m"
echo -e "\033[90mPlatform: $PLATFORM | Service: $SERVICE | Env: $ENVIRONMENT\033[0m"

if [ "$DRY_RUN" = true ]; then
    echo -e "\033[33m⚠️  DRY RUN MODE - No changes will be made\033[0m"
fi

check_prerequisites() {
    local platform=$1
    
    case $platform in
        fly)
            if ! command -v flyctl &> /dev/null; then
                echo -e "\033[31m❌ flyctl not found. Install from https://fly.io/docs/hands-on/install-flyctl/\033[0m"
                return 1
            fi
            
            if ! flyctl auth whoami &> /dev/null; then
                echo -e "\033[31m❌ Not logged in to Fly.io. Run: flyctl auth login\033[0m"
                return 1
            fi
            echo -e "   \033[32m✅ Fly.io CLI ready\033[0m"
            ;;
        railway)
            if ! command -v railway &> /dev/null; then
                echo -e "\033[31m❌ railway CLI not found. Install from https://docs.railway.app/develop/cli\033[0m"
                return 1
            fi
            echo -e "   \033[32m✅ Railway CLI ready\033[0m"
            ;;
        docker|docker-prod)
            if ! command -v docker &> /dev/null; then
                echo -e "\033[31m❌ docker not found\033[0m"
                return 1
            fi
            echo -e "   \033[32m✅ Docker ready\033[0m"
            ;;
    esac
    
    return 0
}

deploy_to_fly() {
    local service=$1
    
    echo -e "\n\033[34m☁️  Deploying to Fly.io...\033[0m"
    
    declare -A configs
    configs["api"]="fly.toml"
    configs["dashboard"]="deploy/fly.dashboard.toml"
    configs["bot"]="fly.toml"
    
    local services
    if [ "$service" = "all" ]; then
        services=("api" "dashboard")
    else
        services=("$service")
    fi
    
    for svc in "${services[@]}"; do
        local config="${configs[$svc]}"
        
        if [ ! -f "$config" ]; then
            echo -e "   \033[33m⚠️  Config not found: $config, skipping $svc\033[0m"
            continue
        fi
        
        echo -e "   Deploying $svc using $config..."
        
        if [ "$DRY_RUN" = true ]; then
            echo -e "   \033[33m[DRY RUN] Would run: flyctl deploy --config $config\033[0m"
        else
            flyctl deploy --config "$config"
            
            if [ $? -eq 0 ]; then
                echo -e "   \033[32m✅ $svc deployed successfully\033[0m"
            else
                echo -e "   \033[31m❌ Failed to deploy $svc\033[0m"
                return 1
            fi
        fi
    done
    
    return 0
}

deploy_to_railway() {
    echo -e "\n\033[34m🚂 Deploying to Railway...\033[0m"
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "   \033[33m[DRY RUN] Would run: railway up\033[0m"
    else
        railway up
        
        if [ $? -eq 0 ]; then
            echo -e "   \033[32m✅ Deployed to Railway successfully\033[0m"
        else
            echo -e "   \033[31m❌ Failed to deploy to Railway\033[0m"
            return 1
        fi
    fi
    
    return 0
}

deploy_to_docker() {
    local service=$1
    local production=$2
    
    local compose_file
    local env_label
    
    if [ "$production" = true ]; then
        compose_file="deploy/docker-compose.prod.yml"
        env_label="Production"
    else
        compose_file="docker-compose.yml"
        env_label="Development"
    fi
    
    echo -e "\n\033[34m🐳 Deploying with Docker Compose ($env_label)...\033[0m"
    
    if [ ! -f "$compose_file" ]; then
        echo -e "   \033[31m❌ Compose file not found: $compose_file\033[0m"
        return 1
    fi
    
    local services=""
    if [ "$service" != "all" ]; then
        services="$service"
    fi
    
    # Pull latest images for production
    if [ "$production" = true ]; then
        echo -e "   Pulling latest images..."
        if [ "$DRY_RUN" = false ]; then
            docker-compose -f "$compose_file" pull $services
        fi
    fi
    
    # Build if needed
    echo -e "   Building services..."
    if [ "$DRY_RUN" = true ]; then
        echo -e "   \033[33m[DRY RUN] Would run: docker-compose -f $compose_file build $services\033[0m"
    else
        docker-compose -f "$compose_file" build $services
    fi
    
    # Deploy
    echo -e "   Starting services..."
    if [ "$DRY_RUN" = true ]; then
        echo -e "   \033[33m[DRY RUN] Would run: docker-compose -f $compose_file up -d $services\033[0m"
    else
        docker-compose -f "$compose_file" up -d $services
        
        if [ $? -eq 0 ]; then
            echo -e "   \033[32m✅ Docker deployment successful\033[0m"
            echo -e "\n   Running containers:"
            docker-compose -f "$compose_file" ps
        else
            echo -e "   \033[31m❌ Docker deployment failed\033[0m"
            return 1
        fi
    fi
    
    return 0
}

show_deployment_info() {
    local platform=$1
    
    echo -e "\n\033[36m📋 Deployment Info:\033[0m"
    
    case $platform in
        fly)
            echo "   Run 'flyctl status' to check deployment status"
            echo "   Run 'flyctl logs' to view logs"
            ;;
        railway)
            echo "   Run 'railway logs' to view logs"
            echo "   Run 'railway open' to open dashboard"
            ;;
        docker)
            echo "   Run 'docker-compose logs -f' to view logs"
            echo "   Run 'docker-compose ps' to check status"
            ;;
        docker-prod)
            echo "   Run 'docker-compose -f deploy/docker-compose.prod.yml logs -f' to view logs"
            ;;
    esac
}

# Check prerequisites
echo -e "\n\033[34m🔍 Checking prerequisites...\033[0m"
if ! check_prerequisites "$PLATFORM"; then
    exit 1
fi

# Execute deployment
SUCCESS=false

case $PLATFORM in
    fly)
        deploy_to_fly "$SERVICE" && SUCCESS=true
        ;;
    railway)
        deploy_to_railway && SUCCESS=true
        ;;
    docker)
        deploy_to_docker "$SERVICE" false && SUCCESS=true
        ;;
    docker-prod)
        deploy_to_docker "$SERVICE" true && SUCCESS=true
        ;;
esac

# Show result
echo -e "\n\033[36m====================================\033[0m"
if [ "$SUCCESS" = true ]; then
    echo -e "\033[32m✅ Deployment completed!\033[0m"
    show_deployment_info "$PLATFORM"
else
    echo -e "\033[31m❌ Deployment failed!\033[0m"
    exit 1
fi
