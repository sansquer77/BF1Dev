#!/bin/bash
# Script de inicialização para Digital Ocean App Platform
# Garante que diretórios necessários existem e ajusta permissões

set -e

echo "🚀 Inicializando BF1Dev 3.0..."

# Criar diretório de dados se não existir
mkdir -p /app/data
mkdir -p /app/backups
mkdir -p /app/logs

# Definir permissões
chmod -R 755 /app/data
chmod -R 755 /app/backups
chmod -R 755 /app/logs

# Ajustar path do banco de dados se estiver rodando em Digital Ocean
if [ -z "$DATABASE_PATH" ]; then
    export DATABASE_PATH="/app/data/bolao_F1.db"
fi

echo "📊 Banco de dados: $DATABASE_PATH"
echo "✅ Inicialização completa"

# Executar Streamlit
exec streamlit run main.py \
    --server.port=${PORT:-8501} \
    --server.address=0.0.0.0 \
    --logger.level=info
