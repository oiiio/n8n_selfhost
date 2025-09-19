#!/bin/bash

# n8n Local Development Manager
# Usage: ./start.sh [up|down|restart|logs|status]

set -e

COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[n8n]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[n8n]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[n8n]${NC} $1"
}

print_error() {
    echo -e "${RED}[n8n]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop and try again."
        exit 1
    fi
}

# Check if required files exist
check_files() {
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        print_error "docker-compose.yml not found!"
        exit 1
    fi
    
    if [[ ! -f "$ENV_FILE" ]]; then
        print_error ".env file not found!"
        exit 1
    fi
}

# Start n8n
start_n8n() {
    print_status "Starting n8n..."
    docker-compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d
    
    if [[ $? -eq 0 ]]; then
        print_success "n8n started successfully!"
        print_status "n8n is available at: http://localhost:5678"
        print_status "Default credentials: admin / password"
        print_warning "Remember to change the default password in production!"
    else
        print_error "Failed to start n8n"
        exit 1
    fi
}

# Stop n8n
stop_n8n() {
    print_status "Stopping n8n..."
    docker-compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" down
    
    if [[ $? -eq 0 ]]; then
        print_success "n8n stopped successfully!"
    else
        print_error "Failed to stop n8n"
        exit 1
    fi
}

# Restart n8n
restart_n8n() {
    print_status "Restarting n8n..."
    stop_n8n
    sleep 2
    start_n8n
}

# Show logs
show_logs() {
    print_status "Showing n8n logs (Press Ctrl+C to exit)..."
    docker-compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs -f n8n
}

# Show status
show_status() {
    print_status "n8n container status:"
    docker-compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps
    
    echo ""
    print_status "Docker container details:"
    docker ps --filter "name=n8n" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

# Main script logic
main() {
    check_docker
    check_files
    
    case "${1:-up}" in
        "up"|"start")
            start_n8n
            ;;
        "down"|"stop")
            stop_n8n
            ;;
        "restart")
            restart_n8n
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        *)
            echo "Usage: $0 [up|down|restart|logs|status]"
            echo ""
            echo "Commands:"
            echo "  up/start   - Start n8n container"
            echo "  down/stop  - Stop n8n container"
            echo "  restart    - Restart n8n container"
            echo "  logs       - Show n8n logs"
            echo "  status     - Show container status"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"