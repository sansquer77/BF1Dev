#!/bin/bash
# Script para facilitar deployment e testes

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Menu principal
show_menu() {
    print_header "BF1Dev 3.0 - Deployment Helper"
    echo ""
    echo "1) Setup ambiente (.env)"
    echo "2) Build Docker image"
    echo "3) Run com Docker Compose (dev)"
    echo "4) Run com Docker (prod)"
    echo "5) Test local (python3)"
    echo "6) Verificar requirements"
    echo "7) Criar backup do banco"
    echo "8) Ver logs"
    echo "9) Stop containers"
    echo "0) Sair"
    echo ""
    read -p "Escolha uma opção: " choice
}

# Setup .env
setup_env() {
    print_header "Setup Ambiente"
    
    if [ -f .env ]; then
        print_error ".env já existe"
        read -p "Sobrescrever? (s/n): " confirm
        if [ "$confirm" != "s" ]; then
            return
        fi
    fi
    
    cp .env.example .env
    print_success ".env criado a partir de .env.example"
    print_info "Edite .env com seus valores:"
    print_info "nano .env"
}

# Build Docker
build_docker() {
    print_header "Build Docker Image"
    
    if [ ! -f Dockerfile ]; then
        print_error "Dockerfile não encontrado"
        return 1
    fi
    
    docker build -t bf1dev:latest .
    print_success "Image bf1dev:latest criada"
}

# Run com Docker Compose
run_compose() {
    print_header "Run com Docker Compose (Dev)"
    
    if [ ! -f docker-compose.yml ]; then
        print_error "docker-compose.yml não encontrado"
        return 1
    fi
    
    if [ ! -f .env ]; then
        print_error ".env não existe - execute opção 1 primeiro"
        return 1
    fi
    
    docker-compose up --build
}

# Run com Docker (Prod)
run_docker() {
    print_header "Run com Docker (Prod)"
    
    if [ ! -f .env ]; then
        print_error ".env não existe - execute opção 1 primeiro"
        return 1
    fi
    
    # Source .env para variáveis
    export $(cat .env | grep -v '^#' | xargs)
    
    docker run -d \
        -p 8501:8501 \
        --name bf1dev_prod \
        -v bf1dev_data:/app/data \
        -v bf1dev_backups:/app/backups \
        -v bf1dev_logs:/app/logs \
        -e DATABASE_PATH=/app/data/bolao_f1.db \
        -e JWT_SECRET="${JWT_SECRET}" \
        -e EMAIL_REMETENTE="${EMAIL_REMETENTE}" \
        -e SENHA_EMAIL="${SENHA_EMAIL}" \
        -e EMAIL_ADMIN="${EMAIL_ADMIN}" \
        bf1dev:latest
    
    print_success "Container bf1dev_prod iniciado"
    print_info "Acesse: http://localhost:8501"
}

# Test local
test_local() {
    print_header "Test Local (Python)"
    
    python3 -c "
import sys
print('Python version:', sys.version)

try:
    import streamlit as st
    print('✓ Streamlit OK')
except:
    print('✗ Streamlit NOT OK')

try:
    import pandas as pd
    print('✓ Pandas OK')
except:
    print('✗ Pandas NOT OK')

try:
    import bcrypt
    print('✓ Bcrypt OK')
except:
    print('✗ Bcrypt NOT OK')

try:
    import jwt
    print('✓ PyJWT OK')
except:
    print('✗ PyJWT NOT OK')

try:
    from db import db_config
    print(f'✓ DB Config OK (path: {db_config.DB_PATH})')
except Exception as e:
    print(f'✗ DB Config ERROR: {e}')
"
    
    print ""
    print_info "Testando imports da aplicação..."
    python3 -c "
try:
    from db.db_utils import init_db, db_connect
    from services.auth_service import create_token
    from services.email_service import enviar_email
    print('✓ All imports OK')
except Exception as e:
    print(f'✗ Import error: {e}')
"
}

# Verificar requirements
check_requirements() {
    print_header "Verificar Requirements"
    
    python3 -m pip check
    
    print_success "Requirements verificados"
}

# Backup do banco
backup_db() {
    print_header "Criar Backup"
    
    if [ ! -f "bolao_f1.db" ]; then
        print_error "Banco de dados não encontrado (bolao_f1.db)"
        return 1
    fi
    
    mkdir -p backups
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    cp bolao_f1.db backups/bolao_f1_${TIMESTAMP}.db
    
    print_success "Backup criado: backups/bolao_f1_${TIMESTAMP}.db"
}

# Ver logs
view_logs() {
    print_header "Logs"
    
    if [ -f bf1dev.log ]; then
        tail -50 bf1dev.log
    else
        print_error "Arquivo de log não encontrado"
    fi
}

# Stop containers
stop_containers() {
    print_header "Stop Containers"
    
    docker-compose down 2>/dev/null || true
    docker stop bf1dev_prod 2>/dev/null || true
    
    print_success "Containers parados"
}

# Main loop
while true; do
    show_menu
    
    case $choice in
        1) setup_env ;;
        2) build_docker ;;
        3) run_compose ;;
        4) run_docker ;;
        5) test_local ;;
        6) check_requirements ;;
        7) backup_db ;;
        8) view_logs ;;
        9) stop_containers ;;
        0) 
            print_info "Saindo..."
            exit 0
            ;;
        *) 
            print_error "Opção inválida"
            ;;
    esac
    
    echo ""
    read -p "Pressione Enter para continuar..."
done
