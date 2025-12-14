#!/bin/bash

# Birthday Wisher - Docker Deployment Script

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🎂 Birthday Wisher - Docker Deployment${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo -e "${YELLOW}Please install Docker from: https://www.docker.com/get-started${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose is not installed!${NC}"
    echo -e "${YELLOW}Please install Docker Compose${NC}"
    exit 1
fi

# Determine docker compose command
if docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo -e "${GREEN}✅ Docker is installed${NC}"
echo ""

# Parse command line arguments
ACTION=${1:-build}

case $ACTION in
    build)
        echo -e "${YELLOW}➜ Building Docker image...${NC}"
        $DOCKER_COMPOSE build
        echo ""
        echo -e "${GREEN}✅ Build complete!${NC}"
        echo -e "${YELLOW}Run './deploy.sh start' to start the application${NC}"
        ;;
        
    start)
        echo -e "${YELLOW}➜ Starting application...${NC}"
        $DOCKER_COMPOSE up -d
        echo ""
        echo -e "${GREEN}✅ Application started!${NC}"
        echo -e "${YELLOW}Access the application at: ${GREEN}http://localhost:8501${NC}"
        echo ""
        echo -e "${YELLOW}View logs with: ${GREEN}./deploy.sh logs${NC}"
        ;;
        
    stop)
        echo -e "${YELLOW}➜ Stopping application...${NC}"
        $DOCKER_COMPOSE down
        echo ""
        echo -e "${GREEN}✅ Application stopped!${NC}"
        ;;
        
    restart)
        echo -e "${YELLOW}➜ Restarting application...${NC}"
        $DOCKER_COMPOSE restart
        echo ""
        echo -e "${GREEN}✅ Application restarted!${NC}"
        ;;
        
    logs)
        echo -e "${YELLOW}➜ Showing logs (Ctrl+C to exit)...${NC}"
        echo ""
        $DOCKER_COMPOSE logs -f
        ;;
        
    status)
        echo -e "${YELLOW}➜ Container status:${NC}"
        echo ""
        $DOCKER_COMPOSE ps
        ;;
        
    clean)
        echo -e "${YELLOW}➜ Cleaning up...${NC}"
        $DOCKER_COMPOSE down -v
        docker system prune -f
        echo ""
        echo -e "${GREEN}✅ Cleanup complete!${NC}"
        ;;
        
    rebuild)
        echo -e "${YELLOW}➜ Rebuilding and restarting...${NC}"
        $DOCKER_COMPOSE down
        $DOCKER_COMPOSE build --no-cache
        $DOCKER_COMPOSE up -d
        echo ""
        echo -e "${GREEN}✅ Rebuild complete!${NC}"
        echo -e "${YELLOW}Access the application at: ${GREEN}http://localhost:8501${NC}"
        ;;
        
    shell)
        echo -e "${YELLOW}➜ Opening shell in container...${NC}"
        docker exec -it birthday-wisher-app /bin/bash
        ;;
        
    *)
        echo -e "${YELLOW}Usage: ./deploy.sh [command]${NC}"
        echo ""
        echo -e "${BLUE}Available commands:${NC}"
        echo -e "  ${GREEN}build${NC}    - Build the Docker image"
        echo -e "  ${GREEN}start${NC}    - Start the application"
        echo -e "  ${GREEN}stop${NC}     - Stop the application"
        echo -e "  ${GREEN}restart${NC}  - Restart the application"
        echo -e "  ${GREEN}logs${NC}     - View application logs"
        echo -e "  ${GREEN}status${NC}   - Show container status"
        echo -e "  ${GREEN}clean${NC}    - Stop and remove containers and volumes"
        echo -e "  ${GREEN}rebuild${NC}  - Rebuild and restart (no cache)"
        echo -e "  ${GREEN}shell${NC}    - Open a shell in the container"
        echo ""
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
