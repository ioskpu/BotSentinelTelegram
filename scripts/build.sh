#!/bin/bash
# Build script for Crypto Sentinel Bot

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

TARGET="${1:-all}"
TAG="${2:-latest}"
PUSH=false
NO_CACHE=""
REGISTRY=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --push) PUSH=true; shift ;;
        --no-cache) NO_CACHE="--no-cache"; shift ;;
        --registry) REGISTRY="$2"; shift 2 ;;
        --tag) TAG="$2"; shift 2 ;;
        frontend|docker|all) TARGET=$1; shift ;;
        *) shift ;;
    esac
done

echo -e "\033[36m🔨 Crypto Sentinel Bot - Build Script\033[0m"
echo -e "\033[36m======================================\033[0m"
echo -e "\033[90mTarget: $TARGET | Tag: $TAG\033[0m"

IMAGE_PREFIX=""
if [ -n "$REGISTRY" ]; then
    IMAGE_PREFIX="$REGISTRY/"
fi

build_frontend() {
    echo -e "\n\033[34m📦 Building Frontend...\033[0m"
    
    if [ ! -d "dashboard" ]; then
        echo -e "\033[31m❌ Dashboard directory not found!\033[0m"
        return 1
    fi
    
    cd dashboard
    
    # Install dependencies
    if [ ! -d "node_modules" ]; then
        echo -e "   Installing dependencies..."
        npm ci --legacy-peer-deps
    fi
    
    # Run linting
    echo -e "   Running linter..."
    npm run lint 2>/dev/null || echo -e "\033[33m   ⚠️  Linting warnings found, continuing...\033[0m"
    
    # Run type check
    echo -e "   Running type check..."
    npm run type-check 2>/dev/null || echo -e "\033[33m   ⚠️  Type warnings found, continuing...\033[0m"
    
    # Build
    echo -e "   Building production bundle..."
    npm run build
    
    if [ $? -eq 0 ]; then
        echo -e "   \033[32m✅ Frontend build complete!\033[0m"
        
        # Show bundle size
        if [ -d "dist" ]; then
            SIZE=$(du -sh dist | cut -f1)
            echo -e "   \033[90m📊 Bundle size: $SIZE\033[0m"
        fi
        cd ..
        return 0
    else
        echo -e "   \033[31m❌ Frontend build failed!\033[0m"
        cd ..
        return 1
    fi
}

build_docker_images() {
    echo -e "\n\033[34m🐳 Building Docker Images...\033[0m"
    
    declare -A images
    images["crypto-sentinel-api"]=".:Dockerfile"
    images["crypto-sentinel-dashboard"]="./dashboard:Dockerfile"
    
    SUCCESS=true
    
    for name in "${!images[@]}"; do
        IFS=':' read -r context dockerfile <<< "${images[$name]}"
        IMAGE_NAME="${IMAGE_PREFIX}${name}:${TAG}"
        
        echo -e "   Building $IMAGE_NAME..."
        
        docker build $NO_CACHE -t "$IMAGE_NAME" -f "$context/$dockerfile" "$context"
        
        if [ $? -eq 0 ]; then
            echo -e "   \033[32m✅ $name built successfully\033[0m"
            
            # Also tag as latest if not already
            if [ "$TAG" != "latest" ]; then
                docker tag "$IMAGE_NAME" "${IMAGE_PREFIX}${name}:latest"
            fi
        else
            echo -e "   \033[31m❌ Failed to build $name\033[0m"
            SUCCESS=false
        fi
    done
    
    if [ "$SUCCESS" = true ]; then
        return 0
    else
        return 1
    fi
}

push_docker_images() {
    echo -e "\n\033[34m📤 Pushing Docker Images...\033[0m"
    
    if [ -z "$REGISTRY" ]; then
        echo -e "   \033[33m⚠️  No registry specified, skipping push\033[0m"
        return 0
    fi
    
    IMAGES=("crypto-sentinel-api" "crypto-sentinel-dashboard")
    
    for name in "${IMAGES[@]}"; do
        IMAGE_NAME="${IMAGE_PREFIX}${name}:${TAG}"
        echo -e "   Pushing $IMAGE_NAME..."
        
        docker push "$IMAGE_NAME"
        
        if [ $? -eq 0 ]; then
            echo -e "   \033[32m✅ $name pushed successfully\033[0m"
        else
            echo -e "   \033[31m❌ Failed to push $name\033[0m"
            return 1
        fi
    done
    
    return 0
}

# Execute build steps
SUCCESS=true

case $TARGET in
    frontend)
        build_frontend || SUCCESS=false
        ;;
    docker)
        build_docker_images || SUCCESS=false
        ;;
    all)
        build_frontend || SUCCESS=false
        if [ "$SUCCESS" = true ]; then
            build_docker_images || SUCCESS=false
        fi
        ;;
esac

# Push if requested
if [ "$SUCCESS" = true ] && [ "$PUSH" = true ]; then
    push_docker_images || SUCCESS=false
fi

# Summary
echo -e "\n\033[36m======================================\033[0m"
if [ "$SUCCESS" = true ]; then
    echo -e "\033[32m✅ Build completed successfully!\033[0m"
    echo -e "\n\033[36m📋 Built images:\033[0m"
    docker images | grep crypto-sentinel || true
else
    echo -e "\033[31m❌ Build failed!\033[0m"
    exit 1
fi
