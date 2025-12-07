#!/bin/bash
# Quick Start - BF1Dev 3.0 Local Execution

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║         🚀 BF1Dev 3.0 - Local Execution Guide              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

echo "✅ Verificação de Pré-requisitos:"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "  ✓ Python $PYTHON_VERSION"
else
    echo "  ✗ Python 3 não encontrado"
    echo "    Instale: https://www.python.org/downloads/"
    exit 1
fi

# Check Streamlit
if python3 -c "import streamlit" 2>/dev/null; then
    STREAMLIT_VERSION=$(python3 -c "import streamlit; print(streamlit.__version__)" 2>/dev/null)
    echo "  ✓ Streamlit $STREAMLIT_VERSION"
else
    echo "  ✗ Streamlit não instalado"
    echo "    Instale com: pip install -r requirements.txt"
    exit 1
fi

# Check Docker (optional)
if command -v docker &> /dev/null; then
    echo "  ✓ Docker $(docker --version | awk '{print $3}')"
else
    echo "  ⓘ Docker não instalado (opcional para docker-compose)"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📋 OPÇÕES DE EXECUÇÃO:"
echo ""
echo "1️⃣  STREAMLIT DIRETO (Recomendado para dev)"
echo "   $ streamlit run main.py"
echo ""
echo "   Então abra: http://localhost:8501"
echo ""
echo "2️⃣  DOCKER COMPOSE (Prod-like local)"
echo "   $ docker-compose up"
echo ""
echo "   Então abra: http://localhost:8501"
echo ""
echo "3️⃣  PYTHON DIRETO (Para testes)"
echo "   $ python3 main.py"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "⚙️  VARIÁVEIS DE AMBIENTE (Opcional):"
echo ""
echo "   Copie .env.example para .env:"
echo "   $ cp .env.example .env"
echo ""
echo "   Edite com seus valores:"
echo "   $ nano .env"
echo ""
echo "   Depois execute:"
echo "   $ source .env"
echo "   $ streamlit run main.py"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "🔍 TROUBLESHOOTING:"
echo ""
echo "  Se der erro de porta em uso:"
echo "  $ streamlit run main.py --server.port 8502"
echo ""
echo "  Se der erro de conexão com DB:"
echo "  $ rm -f bolao_f1.db  # Remove DB antigo"
echo "  $ streamlit run main.py  # Cria novo"
echo ""
echo "  Se der erro de imports:"
echo "  $ pip install -r requirements.txt  # Reinstala deps"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📊 STATUS:"
echo ""
python3 -c "
import sys
try:
    from db import db_config
    from services.auth_service import create_token
    print('  ✓ All imports OK')
    print(f'  ✓ Database: {db_config.DB_PATH}')
    print('  ✓ Pronto para executar!')
except Exception as e:
    print(f'  ✗ Error: {e}')
    sys.exit(1)
"
echo ""
echo "═══════════════════════════════════════════════════════════════"
